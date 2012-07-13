from daisyproducer.documents.models import Document
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from lxml import etree
from os.path import join

import cmislib
import httplib2
import httplib
import os
import re

class ImportError(Exception):
    pass

class Command(BaseCommand):
    args = 'ABACUS_export_file'
    help = 'Import the given file as a new document'
    output_transaction = True

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('No ABACUS Export file specified')

        self.numberOfDocuments = 0

        metadata = {
            "title": "dc/title",
            "author": "dc/creator",
            "date": "dc/date",
            "source": "dc/source",
            "language": "dc/language",
            "source_date": "sbs/auflageJahr",
            "source_edition": "sbs/auflageJahr",
            "source_publisher": "sbs/verlag",
            }
        root = "/AbaConnectContainer/Task/Transaction/DocumentData"

        relaxng_schema = etree.parse(join(settings.PROJECT_DIR, 'erp', 'schema', 'abacus_export.rng'),)
        relaxng = etree.RelaxNG(relaxng_schema)

        for file in args:
            try:
                tree = etree.parse(file)
                relaxng.assertValid(tree)
            except IOError:
                raise CommandError('ABACUS Export file "%s" not found' % file)
            except etree.XMLSyntaxError, e:
                raise CommandError('Cannot parse ABACUS Export file "%s"' % file, e)
            except lxml.etree.DocumentInvalid, e:
                raise CommandError('ABACUS Export file "%s" is not valid' % file, e)

            xpatheval = etree.XPathEvaluator(tree)
            product_number = xpatheval("%s/artikel_nr" % root)[0].text
            try:
                checkout_document(product_number)
            except ImportError, e:
                print e
                continue

            params = dict([(key, xpatheval("%s/MetaData/%s" % (root, value))[0].text) for (key, value) in metadata.items()])
            production_series_number = xpatheval("%s/MetaData/sbs/rucksackNr" % root)[0].text
            if production_series_number != '0':
                params["production_series"] = Document.PRODUCTION_SERIES_CHOICES[1][0]
                params["production_series_number"] = production_series_number
            nodes = xpatheval("%s/MetaData/sbs/reihe" % root)
            reihe = nodes[0].text if nodes else ''
            if production_series_number == '0' and reihe.upper().find('SJW') != -1:
                params['production_series'] = Document.PRODUCTION_SERIES_CHOICES[0][0]
                m = re.search('\d+', reihe) # extract the series number
                if m != None:
                    params['production_series_number'] = m.group(0)
            if xpatheval("%s/MetaData/sbs/Aufwand_A2" % root)[0].text == 'D':
                params["production_source"] = Document.PRODUCTION_SOURCE_CHOICES[0][0]
            document = Document(**params)
            print document
#        document.save()
#            os.remove(file) 

            self.numberOfDocuments += 1

        self.stdout.write('Successfully added %s products.\n' % self.numberOfDocuments)

def checkout_document(product_number):
    url = 'http://pam02.sbszh.ch/alfresco/s/api/cmis'
    user = 'test_pam02_eglic'
    password = 'alfrescotester'
    cmisClient = cmislib.CmisClient(url, user, password)
    repo = cmisClient.defaultRepository

    q = "select * from sbs:produkt where sbs:pProduktNo = '%s'" % product_number
    resultset = repo.query(q)
    if not resultset.hasNext():
        raise ImportError("Product %s not found" % product_number)
    product = resultset.getNext()

    ticket = get_auth_ticket(user, password)
    h = httplib2.Http()

    scriptPath = "/Company%20Home/Data%20Dictionary/Scripts/checkout_product.js"
    url = "http://pam02.sbszh.ch/alfresco/command/script/execute?scriptPath=%s&noderef=%s&ticket=%s" % (scriptPath, product.id, ticket)
    response, content = h.request(url)
    if response.status != httplib.OK:
        tree = etree.HTML(content)
        error_message = tree.xpath("//div[@class='errorMessage']")
        raise ImportError("Checkout of product %s failed\n%s" % (product.name, error_message[0].text))

def get_auth_ticket(user, password):
    url = "http://pam02.sbszh.ch/alfresco/service/api/login?u=%s&pw=%s" % (user, password)
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == httplib.FORBIDDEN:
        raise ImportError("Authorization with Alfresco failed")
    tree = etree.fromstring(content)
    ticket = tree.xpath('/ticket')
    if not ticket:
        raise ImportError("No ticket returned by Alfresco\n%s" % content)
    return ticket[0].text

