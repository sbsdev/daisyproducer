from daisyproducer.documents.models import Document, Version
from django.core.management.base import BaseCommand, CommandError
from os.path import join
from shutil import copyfile

class Command(BaseCommand):
    help = 'Export the newest content for the given product numbers'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'product_numbers',
            nargs='+',
            type=int,
            metavar='ProductNumber',
            help='product number to be exported'
        )

        parser.add_argument(
            '-o', 
            '--output-dir',
            action='store',
            default='/tmp',
            dest='output_dir',
            help='Where to place the content files. This directory must exist and be writable.'
        )

    def handle(self, *args, **options):

        output_dir = options['output_dir']
        verbosity = int(options['verbosity'])
        products_exported = 0

        for product in options['product_numbers']:
            if verbosity >= 1:
                self.stdout.write('Exporting content for %s...\n' % product)

            try:
                document = Document.objects.get(product__identifier=product)
            except Document.DoesNotExist:
                self.stderr.write('Product %s does not exist\n' % product)
                continue

            version = document.latest_version()
            copyfile(version.content.path, join(output_dir, product + ".xml"))
            products_exported += 1

        if verbosity >= 1:
            self.stdout.write("%s products exported\n" % products_exported)

