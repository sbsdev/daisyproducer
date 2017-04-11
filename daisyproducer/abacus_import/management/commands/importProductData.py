from daisyproducer.documents.models import Document, Version, Product
from daisyproducer.abacus_import.management.commands.importABACUS import get_type, get_documents_by_product_number, get_documents_by_source_or_title_source_edition
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import csv
import logging
import re

VALID_PRODUCT_NUMBER_RE = re.compile(u"^(PS|GD|EB|ET)\d{5}$")
VALID_ISBN_RE = re.compile(u"^[0-9-X]{10,18}$")

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import the product numbers in the given file and associate them with existing documents'
    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument(
            'ABACUS_export_file',
            nargs='+',
            help = 'File containing product numbers to be associated with existing documents'
        )

        parser.add_argument(
            '-n', 
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Do a simulation before actually performing the import'
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):

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

        dry_run = options.get('dry_run', False)

        products_imported = 0

        for file in options['ABACUS_export_file']:
            logger.info('Processing "%s"', file)

            reader = csv.reader(open(file))

            warned_sources = set()
            for line in reader:
                product_number, author, title, source_edition, source, verkaufstext = line
            
                if not VALID_PRODUCT_NUMBER_RE.match(product_number):
                    logger.warning('Ignoring invalid product number "%s"', product_number)
                    continue

                # clean the source field
                if source == "keine":
                    source = ""

                # validate the source field
                if source and not VALID_ISBN_RE.match(source):
                    logger.warn('Ignoring invalid ISBN "%s"', source)
                    continue

                # split verkaufstext
                if verkaufstext:
                    lines = verkaufstext.splitlines()
                    if len(lines) >= 2:
                        author = lines[0].strip()
                        title = lines[1].strip()
                    else:
                        logger.warn('Ignoring invalid verkaufstext "%s"', verkaufstext)

                if get_documents_by_product_number(product_number):
                    # the product number is already associated with a document
                    logger.debug('Product number "%s" already registered.', product_number)
                    continue
                elif not get_documents_by_source_or_title_source_edition(source, title, source_edition):
                    if (source, title, source_edition) not in warned_sources:
                        logger.warning('No document for source [%s] or title and source_edition [%s, %s]', source, title, source_edition)
                        warned_sources.add((source, title, source_edition))
                    continue

                documents = get_documents_by_source_or_title_source_edition(source, title, source_edition)
                if len(documents) > 1:
                    logger.error('More than one document for source [%s] or title and source_edition [%s, %s] (%s)', source, title, source_edition, documents)
                document = documents[0]
                # update the product association
                logger.debug('Updating product association ["%s" -> "%s"].', document.title, product_number)
                if not dry_run:
                    Product.objects.create(identifier=product_number, type=get_type(product_number), document=document)
                        
                products_imported += 1
            
        logger.info("%s products imported", products_imported)

