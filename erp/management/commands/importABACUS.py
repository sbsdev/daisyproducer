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

        verbosity = int(options['verbosity'])
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
            except etree.DocumentInvalid, e:
                raise CommandError('ABACUS Export file "%s" is not valid' % file, e)

            evaluator = etree.XPathEvaluator(tree)
            get_key = make_get_key_fn(evaluator)

            product_number = get_key("%s/artikel_nr" % root)
            params = dict([(key, get_key("%s/MetaData/%s" % (root, value))) for (key, value) in metadata.items()])

            if verbosity >= 1:
                self.stdout.write('Processing "%s" [%s]... \n' % (params['title'], product_number))

            daisy_producer = get_key("%s/MetaData/sbs/daisy_producer" % root)
            if daisy_producer != "ja":
                if verbosity >= 2:
                    self.stdout.write('Ignoring "%s" as daisy_producer is set to "%s" \n' % (params['title'], daisy_producer))
                continue

            try:
                checkout_document(product_number)
            except ImportError, e:
                if verbosity >= 2:
                    self.stdout.write('%s\n' % e)
                continue

            production_series_number = get_key("%s/MetaData/sbs/rucksackNr" % root)
            if production_series_number != '0':
                params["production_series"] = Document.PRODUCTION_SERIES_CHOICES[1][0]
                params["production_series_number"] = production_series_number
            reihe = get_key("%s/MetaData/sbs/reihe" % root)
            if production_series_number == '0' and reihe and reihe.upper().find('SJW') != -1:
                params['production_series'] = Document.PRODUCTION_SERIES_CHOICES[0][0]
                m = re.search('\d+', reihe) # extract the series number
                if m != None:
                    params['production_series_number'] = m.group(0)
            if get_key("%s/MetaData/sbs/Aufwand_A2" % root) == 'D':
                params["production_source"] = Document.PRODUCTION_SOURCE_CHOICES[0][0]
            document = Document(**params)
            print document
#        document.save()
#            os.remove(file) 

            self.numberOfDocuments += 1

        self.stdout.write('Successfully added %s products.\n' % self.numberOfDocuments)


def make_get_key_fn(evaluator):
    def get_key(key):
        node = evaluator(key)
        return node[0].text if node else None
    return get_key

def checkout_document(product_number):
    url = 'http://pam02.sbszh.ch/alfresco/s/api/cmis'
    user = 'test_pam02_eglic'
    password = 'alfrescotester'
    cmisClient = cmislib.CmisClient(url, user, password)
    repo = cmisClient.defaultRepository

    # let's see if the product exists at all
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s'" % product_number
    resultset = repo.query(q)
    if not resultset:
        raise ImportError("Product %s not found" % product_number)

    archive_path = "PATH:\"/app:company_home/cm:Produktion/cm:Archiv//*\""
    # we only need to check out products that are archived already
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s' AND CONTAINS('%s')" % (product_number, archive_path)
    resultset = repo.query(q)
    if not resultset:
        # if it isn't in the archive then the product is new or still
        # being worked on. Then we do not need to check anything out,
        # i.e. we are done
        if verbosity >= 2:
            self.stdout.write('Product [%s] is not in archive path [%s], so no need to check it out "%s" \n' % (product_number, archive_path))
        return

    product = resultset[0]

    ticket = get_auth_ticket(user, password)
    h = httplib2.Http()

    scriptPath = "/Company%20Home/Data%20Dictionary/Scripts/checkout_product.js"
    url = "http://pam02.sbszh.ch/alfresco/command/script/execute?scriptPath=%s&noderef=%s&ticket=%s" % (scriptPath, product.id, ticket)
    response, content = h.request(url)
    if response.status != httplib.OK:
        tree = etree.HTML(content)
        error_message = tree.xpath("//div[@class='errorMessage']")
        raise ImportError("Checkout of product %s failed with \"%s\"" % (product.name, error_message[0].text))

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

