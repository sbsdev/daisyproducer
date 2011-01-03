import os
import tempfile
import textwrap
from os.path import join, basename, splitext
from shutil import rmtree
from subprocess import call, Popen, PIPE
import re

import libxml2
import libxslt
import louis
from daisyproducer.version import getVersion
from django.conf import settings
from lxml import etree


def filterBrlContractionhints(file_path):
    """Filter all the brl:contractionhints from the given file_path.
    This is done using an XSLT stylesheet. Return the name of a
    temporary file that contains the filtered content. The caller is
    responsible for removing the temporary file."""
    tmpFile = tempfile.mkstemp(prefix="daisyproducer-", suffix=".xml")[1]
    command = (
        "xsltproc",
        "--output", tmpFile,
        join(settings.PROJECT_DIR, 'documents', 'xslt', 'filterBrlContractionhints.xsl'),
        file_path,
        )
    call(command)
    return tmpFile

class DaisyPipeline:

    @staticmethod
    def validate(file_path):
        """Validate a given file_path using the Validator from the Daisy
        Pipeline. Return an empty string if the validation was
        successful. Return a list of error messages as delivered by
        the Daisy Pipeline otherwise."""
        
        xmlschema_doc = etree.parse(
            join(settings.PROJECT_DIR, 'documents', 'schema', 'minimalSchema.xsd'))
        xmlschema = etree.XMLSchema(xmlschema_doc)
        
        etree.clear_error_log()
        try:
            doc = etree.parse(file_path)
        except etree.XMLSyntaxError, e:
            entries = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            return [("%s on line %s" % (entry.message, entry.line)) for entry in entries]

        if not xmlschema.validate(doc):
            entries = xmlschema.error_log
            return [("%s on line %s" % (entry.message, entry.line)) for entry in entries]

        tmpFile = filterBrlContractionhints(file_path)
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            # FIXME: This requires a version of the pipeline from
            # trunk (>= rev 2480). You could argue that it is
            # pointless to check for a DOCTYPE declaration here as the
            # filterBrlContractionhints above adds it _anyway_. Well
            # let's just leave it in here in case the filter code ever
            # is refactored out.
            join(settings.DAISY_PIPELINE_PATH, 'scripts', 'verify',
                 'ConfigurableValidator.taskScript'),
            "--validatorInputFile=%s" % tmpFile,
            # make sure files with a missing DOCTYPE declaration do
            # not validate. 
            "--validatorInputDelegates=%s" %
            "org.daisy.util.fileset.validation.delegate.impl.NoDocTypeDeclarationDelegate",
            )
        result = map(lambda line: line.replace("file:%s" % file_path, "", 1),
                   map(lambda line: line.replace("[ERROR, Validator]", "", 1), 
                       filter(lambda line: line.find('[ERROR, Validator]') != -1, 
                              Popen(command, stdout=PIPE).communicate()[0].splitlines())))
        os.remove(tmpFile)
        return result
        
    @staticmethod
    def dtbook2pdf(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to pdf"""
        tmpDir = tempfile.mkdtemp(prefix="daisyproducer-")
        fileBaseName = splitext(basename(inputFile))[0]
        latexFileName = join(tmpDir, fileBaseName + ".tex")

        tmpFile = filterBrlContractionhints(inputFile)
        # Transform to LaTeX using pipeline
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'latex', 'DTBookToLaTeX.taskScript'),
            "--input=%s" % tmpFile,
            "--output=%s" % latexFileName,
            "--fontsize=%(font_size)s" % kwargs,
            "--font=%(font)s" % kwargs,
            "--pageStyle=%(page_style)s" % kwargs,
            "--alignment=%(alignment)s" % kwargs,
            "--papersize=%(paper_size)s" % kwargs,
            )
        call(command)
        os.remove(tmpFile)        
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
        call(command) # call LaTeX again to make sure the toc is inserted
        os.rename(pdfFileName, outputFile)
        os.chdir(currentDir)
        rmtree(tmpDir)

    @staticmethod
    def dtbook2xhtml(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to xhtml"""
        tmpFile = filterBrlContractionhints(inputFile)
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'xhtml', 'DtbookToXhtml.taskScript'),
            "--input=%s" % tmpFile,
            "--output=%s" % outputFile,
            )
        for k, v in kwargs.iteritems():
            command += ("--%s=%s" % (k,v),)
        call(command)
        os.remove(tmpFile)

    @staticmethod
    def dtbook2rtf(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to rtf"""
        tmpFile = filterBrlContractionhints(inputFile)
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'text', 'DtbookToRtf.taskScript'),
            "--input=%s" % tmpFile,
            "--output=%s" % outputFile,
            )
        for k, v in kwargs.iteritems():
            command += ("--%s=%s" % (k,v),)
        call(command)
        os.remove(tmpFile)

    @staticmethod
    def dtbook2epub(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to EPUB"""
        tmpFile = filterBrlContractionhints(inputFile)
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'epub', 'OPSCreator.taskScript'),
            "--input=%s" % tmpFile,
            "--output=%s" % outputFile,
            )
        for k, v in kwargs.iteritems():
            command += ("--%s=%s" % (k,v),)
        call(command)
        os.remove(tmpFile)

    @staticmethod
    def dtbook2text_only_fileset(inputFile, outputPath, **kwargs):
        """Transform a dtbook xml file to a Daisy 2.02 Text-Only fileset"""
        tmpFile = filterBrlContractionhints(inputFile)
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'dtb', 'Fileset-DtbookToDaisy202TextOnly.taskScript'),
            "--input=%s" % tmpFile,
            "--outputPath=%s" % outputPath,
            )
        for k, v in kwargs.iteritems():
            command += ("--%s=%s" % (k,v),)
        call(command)
        os.remove(tmpFile)

    @staticmethod
    def dtbook2dtb(inputFile, outputPath, **kwargs):
        """Transform a dtbook xml file to a Daisy Full-Text Full-Audio book"""
        tmpFile = filterBrlContractionhints(inputFile)
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'create_distribute', 'dtb', 'Narrator-DtbookToDaisy.taskScript'),
            "--input=%s" % tmpFile,
            "--outputPath=%s" % outputPath,
            )
        for k, v in kwargs.iteritems():
            command += ("--%s=%s" % (k,v),)
        call(command)
        os.remove(tmpFile)

class Liblouis:

    contractionMap = {
        0 : 'de-ch-g0.utb', 
        1 : 'de-ch-g1.ctb', 
        2 : 'de-ch-g2.ctb'}

    yesNoMap = {
        True : "yes", 
        False : "no" }

    @staticmethod
    def dtbook2brl(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to brl"""
        tmpFile = filterBrlContractionhints(inputFile)
        # prepare xml input for liblouis
        command = (
            "xsltproc",
            join(settings.PROJECT_DIR, 'documents', 'xslt', 'brailleSanitize.xsl'),
            tmpFile,
            )
        p1 = Popen(command, stdout=PIPE)
        # transform to braille
        command = (
            "xml2brl",
            "-CcellsPerLine=%(cells_per_line)s" % kwargs,
            "-ClinesPerPage=%(lines_per_page)s" % kwargs,
            "-CliteraryTextTable=%s" % Liblouis.contractionMap[kwargs['contraction']],
            "-Chyphenate=%s" % Liblouis.yesNoMap[kwargs['hyphenation']],
            "-CprintPages=%s" % Liblouis.yesNoMap[kwargs['show_original_page_numbers']],
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
        f = open(outputFile, 'w')
        p2 = Popen(command, stdin=p1.stdout, stdout=f, 
                   # FIXME: xml2brl creates a temporary file in cwd,
                   # so we have to change directory to a place where
                   # www-data can create temporary files
                   cwd=tempfile.gettempdir())
        p2.communicate()
        f.close()
        os.remove(tmpFile)


class SBSForm:

    @staticmethod
    def dtbook2sbsform(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to sbsform"""
        command = (
            join(settings.DTBOOK2SBSFORM_PATH, 'dtbook2sbsform.sh'),
            "-s:%s" % inputFile,
            "-o:%s" % outputFile,
            )
        kwargs["version"] = getVersion()
        for k, v in kwargs.iteritems():
            if isinstance(v, bool):
                # map True and False to "true()" and "false()"
                command += ("?%s=%s" % (k, "true()" if v else "false()"),)
            elif isinstance(v, int):
                command += ("?%s=%s" % (k, v),)
            else:
                command += ("%s=%s" % (k,v),)
        call(command)
