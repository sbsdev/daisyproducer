from daisyproducer.documents.models import Document, Version
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os.path import join
from shutil import copyfile

class Command(BaseCommand):
    args = ''
    help = 'Export the newest content for the given product numbers'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '-o', 
            '--output-dir',
            action='store',
            default='/tmp',
            dest='output_dir',
            help='Where to place the content files. This directory must exist and be writable.'),
        )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('No product numbers specified')

        output_dir = options['output_dir']
        verbosity = int(options['verbosity'])
        products_exported = 0

        for product in args:
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

