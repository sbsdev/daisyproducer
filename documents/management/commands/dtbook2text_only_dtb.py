import shutil, tempfile, os
from optparse import make_option

from daisyproducer.documents.external import DaisyPipeline, zipDirectory

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

class Command(BaseCommand):
    args = '<dtbook dtbook ...>'
    help = 'Convert the given DTBook files to text-only DAISY books'

    option_list = BaseCommand.option_list + (
        make_option(
            '--outputPath',
            action='store',
            type="string",
            dest='outputPath',
            help='Path where the resulting DTBs are to be stored. If not specified they will be placed alongside the DTBook XML files.'),
        )

    def handle(self, *args, **options):
        outputPath = options['outputPath']
        verbosity = int(options['verbosity'])
        conversions = 0

        for dtbook in args:
            if verbosity >= 2:
                self.stdout.write('Converting %s...\n' % dtbook)
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")
            result = DaisyPipeline.dtbook2text_only_dtb(dtbook, outputDir)
            if result:
                if verbosity >= 1:
                    for error in result:
                        self.stderr.write(error + "\n")
                continue
            if outputPath == None:
                outputPath = os.path.dirname(dtbook)
            fileName, ext =  os.path.splitext(os.path.basename(dtbook))
            zipFileName = os.path.join(outputPath, fileName + ".zip")
            zipDirectory(outputDir, zipFileName, fileName)
            shutil.rmtree(outputDir)
            conversions += 1

        if verbosity >= 2:
            self.stdout.write('Converted %s %s\n' % (conversions, "file" if conversions == 1 else "files"))
        

