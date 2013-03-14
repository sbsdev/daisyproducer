from daisyproducer.documents.external import DaisyPipeline
from daisyproducer.documents.models import Document, Version, Product
from daisyproducer.documents.versionHelper import XMLContent
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from lxml import etree
from os.path import join

import cmislib
import datetime
import httplib
import httplib2
import logging
import os
import re
import tempfile

# This command is meant to be used as a cron job which reads files
# from the order management system and imports the orders or updates
# the meta data if the document has already been created for a
# different order.
#
# Once an order has been imported the corresponding file is deleted.
# This of course fails if the import crashes midway. The file is not
# deleted and the next run of the cron job will try to import the
# order again. The import is not idempotent as some of the actions are
# not inside transactions. The updates in the database (meta data) are
# wrapped inside a transaction. However the changes to the XML file or
# the actions in Alfresco cannot be rolled back. For that reason all
# but a few raise statements have been replaced with logger.error,
# i.e. log an error if isn't fatal and remove the file even if there
# was an error. That way we can at least avoid duplicate checkouts in
# Alfresco but we have essentially no retries.

# TODO 
# - Guard against calling this job again when the previous run isn't
#   finished.
 

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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
        if verbosity == 0:
            # no output
            logging.disable(logging.CRITICAL)
        elif verbosity == 1:
            logger.setLevel(logging.WARNING)
        elif verbosity == 2:
            logger.setLevel(logging.INFO)
        elif verbosity == 3:
            logger.setLevel(logging.DEBUG)

        self.numberOfDocuments = 0

        root = "/AbaConnectContainer/Task/Transaction/DocumentData"

        relaxng_schema = etree.parse(join(settings.PROJECT_DIR, 'integration', 'schema', 'abacus_export.rng'),)
        relaxng = etree.RelaxNG(relaxng_schema)

        for file in args:
            try:
                # Check the validity of the given XML file
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

            # fetch the data from the XML file
            product_number = get_key("%s/artikel_nr" % root)
            params = fetch_params(get_key, root)

            logger.info('Processing "%s" [%s]...', params['title'], product_number)

            # If the XML indicates that this product is not produced with Daisy Producer ignore
            # this file
            daisy_producer = get_key("%s/MetaData/sbs/daisy_producer" % root)
            if daisy_producer != "ja":
                logger.debug('Ignoring "%s" as daisy_producer is set to "%s"', params['title'], daisy_producer)
                continue

            product_number_has_been_seen_before = False
            if get_documents_by_product_number(product_number):
                # If the order has been imported before just update the meta data of the existing order
                product_number_has_been_seen_before = True
                documents = get_documents_by_product_number(product_number)
                # there should only ever be one document here. Make sure this is so
                if len(documents) > 1:
                    logger.error('There is more than one document for the given product %s (%s)', product_number, documents)
                document = documents[0]
                logger.debug('Document "%s" for order number "%s" has already been imported.', document.title, product_number)
                update_document(documents, document, params)
            elif get_documents_by_source_or_title_source_edition(
                params['source'], params['title'], params['source_edition']):
                # check if the book has been produced for another order
                documents = get_documents_by_source_or_title_source_edition(
                    params['source'], params['title'], params['source_edition'])
                # what if there are multiple documents that match the query?
                if len(documents) > 1:
                    logger.error('There is more than one document for the given source [%s] or title and source_edition [%s, %s] (%s)', 
                                 params['source'], params['title'], params['source_edition'], documents)
                document = documents[0]
                logger.debug('Document "%s" has already been imported for a different product.', document.title)
                update_document(documents, document, params)
                # update the product association
                logger.debug('Updating product association ["%s" -> "%s"].', document.title, product_number)
                Product.objects.create(identifier=product_number, type=get_type(product_number), document=document)
            else:
                # If the the order hasn't been imported before create the new order
                logger.debug('Document "%s" has not yet been imported. Creating document for product "%s".', params['title'], product_number)
                # create and save the document
                document = Document.objects.create(**params)
                # create the product association
                Product.objects.create(identifier=product_number, type=get_type(product_number), document=document)
                # create an empty xml
                update_xml_with_metadata(document)

            logger.debug('Import complete. Removing file "%s"', file)
#            os.remove(file) 

            # If the order has been archived before fetch the xml from the archive
            fetch_xml(document, product_number)
            
            # if the product_number has never been seen before then we are talking about a new
            # production, i.e. try to check out the document in the archive
            if not product_number_has_been_seen_before:
                checkout_document(product_number)

            self.numberOfDocuments += 1

        self.stdout.write('Successfully added %s products.\n' % self.numberOfDocuments)

def get_documents_by_product_number(product_number):
    return Document.objects.filter(product__identifier=product_number)

def get_documents_by_source_or_title_source_edition(source, title, source_edition):
    if source:
        return Document.objects.filter(source=source)
    else:
        # in case there is no ISBN number we hope that title and
        # source_edition is unique enough. If that is not the case,
        # i.e. the title or the source_edition was misspelled we have
        # bigger problems anyway
        return Document.objects.filter(title=title, source_edition=source_edition)

def fetch_xml(document, product_number):
    if already_archived(product_number):
        logger.debug('Product has already been archived. Update XML with content from archive.')
        update_xml_with_content_from_archive(document, product_number)

def update_document(queryset, document, params):
    if params_changed(document, params):
        logger.debug('Import params differ from document meta data. Updating meta data with %s.', params)
        queryset.update(**params)
        # update the meta data
        update_xml_with_metadata(document, **params)

def get_type(product_number):
    type = None
    if product_number.startswith('PS'):
        type = 0
    elif product_number.startswith('GD'):
        type = 1
    elif product_number.startswith('EB'):
        type = 2
    return type

def get_abacus_user():
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(username='abacus')
    except User.DoesNotExist:
        user = User.objects.create_user('abacus', 'root@xmlp')
    return user

def params_changed(document, params):
    old_params = model_to_dict(document)
    changed_params = [key for key in old_params.keys() if params.has_key(key) and old_params[key] != params[key]]
    if changed_params:
        logger.debug('Changed params: %s [%s -> %s]', changed_params, [old_params[key] for key in changed_params], [params[key] for key in changed_params])
    return any(changed_params)

def update_xml_with_metadata(document, **params):
    user = get_abacus_user()
    if document.version_set.count() == 0:
        # create an initial version
        contentString  = XMLContent.getInitialContent(document)
        content = ContentFile(contentString)
        version = Version.objects.create(
            comment = "Initial version created from meta data",
            document = document,
            created_by = user)
        version.content.save("initial_version.xml", content)
    else:
        # create a new version with the new content
        xmlContent = XMLContent(document.latest_version())
        contentString = xmlContent.getUpdatedContent(**params)
        content = ContentFile(contentString)
        version = Version.objects.create(
            comment = "Updated version due to meta data change",
            document = document,
            created_by = user)
        version.content.save("updated_version.xml", content)

def validate_content(fileName, contentMetaData):
    # make sure the uploaded version is valid xml
    exitMessages = DaisyPipeline.validate(fileName)
    if exitMessages:
        return exitMessages
    # make sure the meta data of the uploaded version corresponds
    # to the meta data in the document
    xmlContent = XMLContent()
    try:
        errorList = xmlContent.validateContentMetaData(fileName , **contentMetaData)
    except etree.XMLSyntaxError as e:
        return "The uploaded file is not a valid DTBook XML document:" + e.message
    if errorList:
        return "; ".join(
            ("The meta data '%s' in the uploaded file does not correspond to the value in the document: '%s' instead of '%s'" % errorTuple for errorTuple in errorList))

def update_xml_with_content_from_archive(document, product_number):
    user = get_abacus_user()
    contentString = get_document_content(product_number)
    if not contentString:
        return
    # fix meta data
    xsl = etree.parse(os.path.join(settings.PROJECT_DIR, 'integration', 'xslt', 'fixMetaData.xsl'))
    stylesheet_params = dict((k, v) for k, v in model_to_dict(document).iteritems() 
                             if k in ('date', 'identifier', 'production_source'))
    stylesheet_params['date'] = stylesheet_params['date'].isoformat()
    stylesheet_params.update(((k, "'%s'" % v)) for (k, v) in stylesheet_params.iteritems())
    transform = etree.XSLT(xsl)
    fixed_tree = transform(etree.fromstring(contentString), **stylesheet_params)
    contentString = etree.tostring(fixed_tree, xml_declaration=True, encoding='utf-8')
    # write content to file
    tmpFile, tmpFileName = tempfile.mkstemp(prefix="daisyproducer-", suffix=".xml")
    tmpFile = os.fdopen(tmpFile,'w')
    tmpFile.write(contentString)
    tmpFile.close()
    validation_problems = validate_content(tmpFileName, model_to_dict(document))
    if validation_problems:
        logger.critical('Archived XML is not valid. Fails with %s', validation_problems)
        return 
    os.remove(tmpFileName)
    content = ContentFile(contentString)
    version = Version.objects.create(
        comment = "Updated version due fetch from archive",
        document = document,
        created_by = user)
    version.content.save("updated_version.xml", content)
    # also update the content in ueberarbeitung
    update_xml_in_ueberarbeitung(product_number, contentString)

def update_xml_in_ueberarbeitung(product_number, contentString):
    path = "PATH:\"/app:company_home/cm:Produktion/cm:Neuproduktion/cm:Überarbeiten//*\""
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s' AND CONTAINS('%s')" % (product_number, path)
    resultset = cmis_request(q)
    if not resultset:
        logger.error("Product %s not found in Überarbeiten", product_number)
        return
    product = resultset[0]
    book = product.getParent()
    isDaisyFile = lambda child: child.properties['cmis:objectTypeId'] == 'D:sbs:daisyFile'
    resultset = filter(isDaisyFile, book.getChildren())
    if not resultset:
        logger.error("No content found for product %s", product_number)
        return
    document = resultset[0]
    latest_document = document.getLatestVersion()
    stream = latest_document.getContentStream()
    stream.write(contentString)
    stream.close()

def fetch_params(get_key, root):
    metadata = {
        "title": "dc/title",
        "author": "dc/creator",
        "date": "dc/date",
        "source": "dc/source",
        "language": "dc/language",
#        "source_date": "sbs/auflageJahr",
        "source_edition": "sbs/auflageJahr",
        "source_publisher": "sbs/verlag",
        }
    params = dict([(key, get_key("%s/MetaData/%s" % (root, value))) for (key, value) in metadata.items()])
    params['date'] = datetime.datetime.strptime(params['date'], '%Y-%m-%d').date()
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
    # if there is an element named verkaufstext then use part of that
    # as the title and the author
    verkaufstext = get_key("%s/MetaData/sbs/verkaufstext" % root)
    if verkaufstext:
        # the schema test makes sure that there are at least two elems
        # in the verkaufstext
        params["author"] = verkaufstext.split('[xx]')[0].strip()
        params["title"] = verkaufstext.split('[xx]')[1].strip()
    return params

def cmis_request(q):
    url = 'http://pam02.sbszh.ch/alfresco/s/api/cmis'
    user = 'test_pam02_eglic'
    password = 'alfrescotester'
    cmisClient = cmislib.CmisClient(url, user, password)
    repo = cmisClient.defaultRepository

    resultset = repo.query(q)
    return resultset
    
def already_archived(product_number):
    archive_path = "PATH:\"/app:company_home/cm:Produktion/cm:Archiv//*\""
    # we only need to check out products that are archived already
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s' AND CONTAINS('%s')" % (product_number, archive_path)
    resultset = cmis_request(q)
    return resultset

def make_get_key_fn(evaluator):
    def get_key(key):
        node = evaluator(key)
        return node[0].text if node and node[0].text else ''
    return get_key

def get_document_content(product_number):
    # let's see if the product exists at all
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s'" % product_number
    cmis_request(q)
    resultset = cmis_request(q)
    if not resultset:
        logger.error("Product %s not found", product_number)
        return
    product = resultset[0]
    book = product.getParent()
    isDaisyFile = lambda child: child.properties['cmis:objectTypeId'] == 'D:sbs:daisyFile'
    resultset = filter(isDaisyFile, book.getChildren())
    if not resultset:
        logger.error("No content found for product %s", product_number)
        return
    document = resultset[0]
    latest_document = document.getLatestVersion()
    stream = latest_document.getContentStream()
    content = stream.read()
    stream.close()
    return content

def checkout_document(product_number):
    # let's see if the product exists at all
    q = "select * from sbs:produkt where sbs:pProduktNo = '%s'" % product_number
    cmis_request(q)
    resultset = cmis_request(q)
    if not resultset:
        logger.error("Product %s not found", product_number)
        return

    if not already_archived(product_number):
        # if it isn't in the archive then the product is new or still
        # being worked on. Then we do not need to check anything out,
        # i.e. we are done
        logger.debug('Product [%s] is not in archive path [%s], so no need to check it out "%s"', product_number, archive_path)
        return

    product = resultset[0]

    ticket = get_auth_ticket()
    if not ticket:
        return
    h = httplib2.Http()

    scriptPath = "/Company%20Home/Data%20Dictionary/Scripts/checkout_product.js"
    url = "http://pam02.sbszh.ch/alfresco/command/script/execute?scriptPath=%s&noderef=%s&ticket=%s" % (scriptPath, product.id, ticket)
    response, content = h.request(url)
    if response.status != httplib.OK:
        tree = etree.HTML(content)
        error_message = tree.xpath("//div[@class='errorMessage']")
        logger.warning("Checkout of product %s failed with \"%s\"", product.name, error_message[0].text)

def get_auth_ticket():
    user = 'test_pam02_eglic'
    password = 'alfrescotester'
    url = "http://pam02.sbszh.ch/alfresco/service/api/login?u=%s&pw=%s" % (user, password)
    h = httplib2.Http()
    response, content = h.request(url)
    if response.status == httplib.FORBIDDEN:
        logger.error("Authorization with Alfresco failed")
        return
    tree = etree.fromstring(content)
    ticket = tree.xpath('/ticket')
    if not ticket:
        logger.error("No ticket returned by Alfresco\n%s", content)
        return
    return ticket[0].text

