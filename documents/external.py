from daisyproducer import settings
from os.path import join, basename, splitext
from shutil import rmtree
from subprocess import call, Popen, PIPE
from tempfile import mkdtemp
import os

class DaisyPipeline:

    @staticmethod
    def validate(file_path):
        """Validate a given file_path using the Validator from the Daisy
        Pipeline. Return an empty string if the validation was
        successful. Return a list of error messages as delivered by
        the Daisy Pipeline otherwise."""
        command = (
            "%s/pipeline.sh" % settings.DAISY_PIPELINE_PATH,
            "%s/%s" %  (
                settings.DAISY_PIPELINE_PATH, 
                'scripts/verify/DTBookValidator.taskScript'),
            "--input=%s" % file_path
            )
        return filter(lambda line: line.find('ERROR') != -1, 
                      Popen(command, stdout=PIPE).communicate()[0].splitlines())
        
    @staticmethod
    def dtbook2pdf(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to pdf"""
        tmpDir = mkdtemp()
        fileBaseName = splitext(basename(inputFile))[0]
        latexFileName = join(tmpDir, fileBaseName + ".tex")
        # Transform to LaTeX using pipeline
        command = (
            "%s/pipeline.sh" % settings.DAISY_PIPELINE_PATH,
            "%s/%s" %  (
                settings.DAISY_PIPELINE_PATH, 
                '/scripts/create_distribute/latex/DTBookToLaTeX.taskScript'),
            "--input=%s" % inputFile,
            "--output=%s" % latexFileName,
            "--fontsize=%(fontSize)s" % kwargs,
            "--font=%(font)s" % kwargs,
            "--pageStyle=%(pageStyle)s" % kwargs,
            "--alignment=%(alignment)s" % kwargs,
            "--papersize=%(paperSize)s" % kwargs)
        call(command)
        # Transform to pdf using xelatex
        pdfFileName = join(tmpDir, fileBaseName + ".pdf")
        currentDir = os.getcwd()
        os.chdir(tmpDir)
        command = (
            "xelatex",
            "-halt-on-error",
            latexFileName
            )
        call(command)
        os.rename(pdfFileName, outputFile)
        os.chdir(currentDir)
        rmtree(tmpDir)
