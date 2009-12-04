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
            "--fontsize=%(font_size)s" % kwargs,
            "--font=%(font)s" % kwargs,
            "--pageStyle=%(page_style)s" % kwargs,
            "--alignment=%(alignment)s" % kwargs,
            "--papersize=%(paper_size)s" % kwargs,
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

    @staticmethod
    def dtbook2xhtml(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to xhtml"""
        command = (
            "%s/pipeline.sh" % settings.DAISY_PIPELINE_PATH,
            "%s/%s" %  (
                settings.DAISY_PIPELINE_PATH, 
                '/scripts/create_distribute/xhtml/DtbookToXhtml.taskScript'),
            "--input=%s" % inputFile,
            "--output=%s" % outputFile,
            # "--daisyNoterefs=%(daisyNoterefs)s" % kwargs,
            # "--genToc=%(genToc)s" % kwargs,
            # "--genChunks=%(genChunks)s" % kwargs,
            )
        call(command)

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

import louis
import libxml2
import libxslt
import string
import textwrap

class SBSForm:
    wrapper = textwrap.TextWrapper(width=80, initial_indent=' ', subsequent_indent=' ')

    nodeName = None

    modeMap = {
        'plain_text' : louis.plain_text, 
        'italic' : louis.italic, 
        'underline' : louis.underline, 
        'bold' : louis.bold, 
        'computer_braille' : louis.computer_braille}

    @staticmethod
    def translate(ctx, str, translation_table, mode=None):
        global nodeName
        
        try:
            pctxt = libxslt.xpathParserContext(_obj=ctx)
            ctxt = pctxt.context()
            tctxt = ctxt.transformContext()
            nodeName = tctxt.insertNode().name
        except:
            pass

        typeform = len(str)*[SBSForm.modeMap[mode]] if mode else None
        braille = louis.translate([translation_table], str.decode('utf-8'), typeform=typeform)[0]
        braille = braille.encode('utf-8')
        return SBSForm.wrapper.fill(braille)


    @staticmethod
    def dtbook2sbsform(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to sbsform"""
        styledoc = libxml2.parseFile(
            join(settings.PROJECT_DIR, 'documents', 'xslt', 'dtbook2sbsform.xsl'))
        style = libxslt.parseStylesheetDoc(styledoc)
        doc = libxml2.parseFile(inputFile)
        # copy the content of kwargs into a new dict map True and False to 1 and 0 and quote the values
        kwargs.update([(k, 1) for (k, v) in kwargs.iteritems() if v == True])
        kwargs.update([(k, 0) for (k, v) in kwargs.iteritems() if v == False])
        params = dict([(k, "'%s'" % v) for (k, v) in kwargs.iteritems()])
        params["translation_table"] = "'" + Liblouis.contractionMap[kwargs['contraction']] + "'"
        params["version"] = "'2009-12-04'"
        result = style.applyStylesheet(doc, params)
        style.saveResultToFilename(outputFile, result, 0)
        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()

libxslt.registerExtModuleFunction("translate", "http://liblouis.org/liblouis", SBSForm.translate)
