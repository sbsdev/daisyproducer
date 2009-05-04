from django.conf import settings
from os.path import join, basename, splitext
from shutil import rmtree
from subprocess import call, Popen, PIPE
from tempfile import mkdtemp, gettempdir
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
                'scripts/verify/DTBookValidator.taskScript',),
            "--input=%s" % file_path,
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
            "--papersize=%(paperSize)s" % kwargs,
            )
        call(command)
        # Transform to pdf using xelatex
        pdfFileName = join(tmpDir, fileBaseName + ".pdf")
        currentDir = os.getcwd()
        os.chdir(tmpDir)
        command = (
            "xelatex",
            "-halt-on-error",
            latexFileName,
            )
        call(command)
        os.rename(pdfFileName, outputFile)
        os.chdir(currentDir)
        rmtree(tmpDir)

class Liblouis:

    contractionMap = {
        0 : 'de-de-g0.utb', 
        1 : 'de-de-g1.ctb', 
        # FIXME: the current release of liblouis doesn't support
        # german grade 2. Adapt this table as soon as it has support
        # for grade 2
        2 : 'de-de-g1.ctb'}

    yesNoMap = {
        True : "yes", 
        False : "no" }

    @staticmethod
    def dtbook2brl(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to brl"""
        # prepare xml input for liblouis
        command = (
            "xsltproc",
            join(settings.PROJECT_DIR, 'documents', 'xslt', 'brailleSanitize.xsl'),
            inputFile,
            )
        p1 = Popen(command, stdout=PIPE)
        # transform to braille
        command = (
            "xml2brl",
            "-CcellsPerLine=%(cellsPerLine)s" % kwargs,
            "-ClinesPerPage=%(linesPerPage)s" % kwargs,
            "-CliteraryTextTable=%s" % Liblouis.contractionMap[kwargs['contraction']],
            "-Chyphenate=%s" % Liblouis.yesNoMap[kwargs['hyphenation']],
            "-CprintPages=%s" % Liblouis.yesNoMap[kwargs['showOriginalPageNumbers']],
            "-Cinterpoint=no",
            "-CnewEntries=no",
            "-Cinterline=no",
            "-CinputTextEncoding=utf8",
            "-CoutputEncoding=ascii8",
            "-CbraillePageNumberAt=bottom",
            "-CprintPageNumberAt=top",
            "-CbeginningPageNumber=1",
            "-Cparagraphs=yes",
            "-CbraillePages=yes",
            "-CfileEnd=\"^z\"",
            # FIXME: find a solution on how to pass these values
            # r"-CpageEnd=\f",
            # r"-ClineEnd=\n",
            "-CsemanticFiles=dtbook.sem",
            "-CinternetAccess=no",
            )
        p2 = Popen(command, stdin=p1.stdout, stdout=PIPE, 
                   # FIXME: xml2brl creates a temporary file in cwd,
                   # so we have to change directory to a place where
                   # www-data can create temporary files
                   cwd=gettempdir())
        # transform to braille
        command = (
            "tr",
            "'[:lower:]'",
            "'[:upper:]'",
            )
        f = open(outputFile, 'w')
        p3 = Popen(command, stdin=p2.stdout, stdout=f)
        p3.communicate()
        f.close()
        
