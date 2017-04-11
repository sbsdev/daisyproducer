import shutil, tempfile, os, csv

from daisyproducer.documents.external import DaisyPipeline, zipDirectory

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Convert the given DTBook files to text-only DAISY books'

    def add_arguments(self, parser):
        parser.add_argument(
            'dtbook_files',
            nargs='+',
            metavar='DTBook',
            help='DTBook file to be exported'
        )

        parser.add_argument(
            '--outputPath',
            action='store',
            dest='outputPath',
            help='Path where the resulting DTBs are to be stored. If not specified they will be placed alongside the DTBook XML files.'
        )

        parser.add_argument(
            '--fileNameMapping',
            action='store',
            dest='fileNameMapping',
            help='Path to a csv that maps DTBook filename to a given filename for the output file. Column 0 contains the file name of the DTBook file. Column 1 contains the name of the DTB file. All other columns are ignored'),

    def handle(self, *args, **options):
        outputPath = options['outputPath']
        verbosity = int(options['verbosity'])
        fileNameMapping = options['fileNameMapping']

        mapping ={}
        if fileNameMapping:
            reader = csv.reader(open(fileNameMapping))
            for line in reader:
                source, dest = line[:2]
                mapping[source] = dest

        conversions = 0

        for dtbook in options['dtbook_files']:
            if verbosity >= 1:
                self.stdout.write('Converting %s...\n' % dtbook)
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")
            result = DaisyPipeline.dtbook2text_only_dtb(
                dtbook, outputDir,
                # we assume that there are no images
                images=[])
            if result:
                for error in result:
                    self.stderr.write(error + "\n")
                continue
            if outputPath == None:
                outputPath = os.path.dirname(dtbook)
            fileName, ext = os.path.splitext(os.path.basename(dtbook))
            if fileNameMapping:
                fileName = mapping[fileName]
            if verbosity >= 2:
                self.stdout.write('Mapping %s to %s\n' % (dtbook, fileName))
                self.stdout.flush()
                
            zipFileName = os.path.join(outputPath, fileName + ".zip")
            zipDirectory(outputDir, zipFileName, fileName)
            shutil.rmtree(outputDir)
            conversions += 1

        if verbosity >= 1:
            self.stdout.write('Converted %s %s of %s\n' % (conversions, "file" if conversions == 1 else "files", len(args)))
        

