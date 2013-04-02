from daisyproducer.documents.external import DaisyPipeline, zipDirectory
from daisyproducer.documents.models import Document, Version
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os.path import join
from shutil import copyfile
import tempfile
import shutil

class Command(BaseCommand):
    args = ''
    help = 'Export a text only DTB for the given product numbers'
    
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
                self.stdout.write('Exporting text only DTB for %s...\n' % product)

            try:
                document = Document.objects.get(product__identifier=product)
            except Document.DoesNotExist:
                self.stderr.write('Product %s does not exist\n' % product)
                continue

            inputFile = document.latest_version().content.path
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

            transformationErrors = DaisyPipeline.dtbook2text_only_dtb(inputFile, outputDir)
            if transformationErrors:
                print transformationErrors

            zipFile = join(output_dir, product + ".zip")
            zipDirectory(outputDir, zipFile, product)
            shutil.rmtree(outputDir)

            products_exported += 1

        if verbosity >= 1:
            self.stdout.write("%s products exported\n" % products_exported)

