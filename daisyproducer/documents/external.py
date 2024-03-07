import requests
import logging
import louis
import math
import os
import re
import subprocess
import tempfile
import zipfile

from os.path import join, basename, splitext
from PyPDF2 import PdfFileReader
from shutil import rmtree, copyfile
from subprocess import call, Popen, PIPE, check_output

from django.conf import settings
import daisyproducer.documents.pipeline2.client2 as client2
from daisyproducer.version import getVersion

logging.config.fileConfig(join(settings.PROJECT_DIR, 'logging.conf'))
logger = logging.getLogger(__name__)

class LatexError(Exception):
    pass

def filterBrlContractionhints(file_path):
    """Filter all the brl:contractionhints from the given file_path.
    This is done using an XSLT stylesheet. Return the name of a
    temporary file that contains the filtered content. The caller is
    responsible for removing the temporary file."""
    tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".xml",
                                          delete=False)
    with open(file_path) as infile, tmpFile as outfile:
        p1 = applyXSL('filterBrlContractionhints.xsl', stdin=infile, stdout=outfile)
        p1.communicate()
    return tmpFile.name

def applyXSL(xsl, *args, **params):
    stdin = params.pop('stdin', None)
    stdout = params.pop('stdout', None)
    stderr = params.pop('stderr', None)
    command = (
        "java",
        "-jar", join('/usr', 'share', 'java', 'Saxon-HE.jar'),
        "-xsl:%s" % join(settings.PROJECT_DIR, 'documents', 'xslt', xsl),
        "-s:-")
    command = command + tuple(args)
    command = command + tuple(["%s=%s" % (key,value) for key,value in params.iteritems()])
    return Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)

def isCompactStyle(inputFile):
    """Given an `inputFile` determine whether it should be rendered using
    compactStyle. Return `true` if the `inputFile` only contains
    `level1`. Return `true` if the `inputFile` contains `level2` but
    all `h2` are empty. Return `false` otherwise."""
    command = (
        "java",
        "-jar", join('/usr', 'share', 'java', 'Saxon-HE.jar'),
        "-xsl:%s" % join(settings.PROJECT_DIR, 'documents', 'xslt', 'isCompactStyle.xsl'),
        "-s:%s" % inputFile
        )
    return check_output(command)=="true"


def generatePDF(inputFile, outputFile, images, taskscript='DTBookToLaTeX.taskScript', **kwargs):
    tmpDir = tempfile.mkdtemp(prefix="daisyproducer-")
    fileBaseName = splitext(basename(inputFile))[0]
    latexFileName = join(tmpDir, fileBaseName + ".tex")

    # map True and False to "true" and "false"
    kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])

    # when the page style is not explicitely requested check if the
    # book should be rendered using compact style
    if kwargs['page_style'] == "plain" and isCompactStyle(inputFile):
        kwargs['page_style'] = "compact"

    # Transform to LaTeX using pipeline
    command = (
        join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
        join(settings.DAISY_PIPELINE_PATH, 'scripts',
             'create_distribute', 'latex', taskscript),
        "--input=%s" % inputFile,
        "--output=%s" % latexFileName,
        "--fontsize=%(font_size)s" % kwargs,
        "--font=%(font)s" % kwargs,
        "--backupFont=Arial",
        "--backupUnicodeRanges=Arabic,Hebrew,Cyrillic,GreekAndCoptic",
        "--pageStyle=%(page_style)s" % kwargs,
        "--alignment=%(alignment)s" % kwargs,
        "--stocksize=%(stock_size)s" % kwargs,
        "--line_spacing=%(line_spacing)s" % kwargs,
        "--replace_em_with_quote=%(replace_em_with_quote)s" % kwargs,
        "--paperwidth=%(paperwidth)s" % kwargs if 'paperwidth' in kwargs else None,
        "--paperheight=%(paperheight)s" % kwargs if 'paperheight' in kwargs else None,
        "--left_margin=%(left_margin)s" % kwargs if 'left_margin' in kwargs else None,
        "--right_margin=%(right_margin)s" % kwargs if 'right_margin' in kwargs else None,
        "--top_margin=%(top_margin)s" % kwargs if 'top_margin' in kwargs else None,
        "--bottom_margin=%(bottom_margin)s" % kwargs if 'bottom_margin' in kwargs else None,
        "--endnotes=%(end_notes)s" % kwargs if 'end_notes' in kwargs else None,
        "--image_visibility=%(image_visibility)s" % kwargs if 'image_visibility' in kwargs else None,
        )
    command = filter(None, command) # filter out empty arguments
    call(command)
    # Transform to pdf using xelatex
    pdfFileName = join(tmpDir, fileBaseName + ".pdf")
    for image in images:
        copyfile(image.content.path, join(tmpDir, basename(image.content.path)))
    currentDir = os.getcwd()
    os.chdir(tmpDir)
    command = (
         # use latexmk to make sure latex is run enough times so that toc and all the page refs are properly resolved
        "latexmk",
        "-interaction=batchmode",
        "-xelatex",
        latexFileName,
        )
    try:
        check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        message = "{1}\n{0}\n{1}".format(e.output, "%"*50)
        logger.error("latexmk failed with exit code %s and the following output:\n%s", e.returncode, message)
        # if the call failed something is wrong. Leave the wreckage
        # around for later analysis
        raise LatexError("The PDF could not be generated. Is maybe an image missing?")

    os.rename(pdfFileName, outputFile)
    os.chdir(currentDir)
    rmtree(tmpDir)

def zipDirectory(directory, zipFileName, document_title=None):
    outputFile = zipfile.ZipFile(zipFileName, 'w')
    cwd = os.getcwd()
    os.chdir(directory)
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            # zipFile support in Python has a few weak spots: Older
            # Pythons die if the filename or the arcname that is
            # passed to ZipFile.write is not in the right encoding
            outputFile.write(
                os.path.join(dirpath, filename), 
                os.path.join(document_title, dirpath, filename) if document_title else None)
    outputFile.close()
    os.chdir(cwd)

def saxon9he(source, xsl, *args, **params):
    command = (
        "java",
        "-jar", join(settings.EXTERNAL_PATH, 'dtbook2sbsform', 'lib', 'saxon9he.jar'),
        "-xsl:%s" % xsl,
        "-s:%s" % source)
    command = command + tuple(args)
    command = command + tuple(["%s=%s" % (key,value) for key,value in params.iteritems()])
    return Popen(command, stderr=PIPE, stdout=PIPE)

class Jing:
    @staticmethod
    def filter_output(lines):
        p = re.compile(r'^.*:([0-9]+):[0-9]+: (error|fatal): (.*)$')
        return [p.sub(r'line \1: \3', line) for line in lines if p.match(line)]

    @staticmethod
    def validate(source, schema):
        command = ("jing", schema, source)
        return Jing.filter_output(list(Popen(command, stdout=PIPE).stdout))

class DaisyPipeline:

    @staticmethod
    def replace_file_references(lines, file_path):
        return [line.replace("file:%s" % file_path, "line: ", 1) for line in lines]

    @staticmethod
    def filter_output(lines):
        return [line.replace("[ERROR, Validator]", "", 1).strip() 
                for line in lines
                # find all lines that contain an error
                if line.find('[ERROR, Validator]') != -1 
                # but drop lines that just announce some more error messages
                and line.find('[ERROR, Validator] assertion failed:') == -1 
                and line.find('[ERROR, Validator] report:') == -1 
                # include lines which are indented by two spaces. Apparently the validator uses this to
                # announce errors
                or line.find('  [') != -1]

    @staticmethod
    def validate(file_path):
        """Validate a given file_path using the Validator from the Daisy
        Pipeline. Return an empty string if the validation was
        successful. Return a list of error messages as delivered by
        the Daisy Pipeline otherwise."""

        result = Jing.validate(file_path, join(settings.PROJECT_DIR, 'documents', 'schema', 'dtbook-2005-3-sbs.rng'))
        if result: return result
        # Validate using Schematron tests. We have to do this before the
        # @brl:* attributes are filtered out.
        # FIXME: don't perform this check if we're validation against the
        # '2005-3-sbs-minimal' variant
        result = saxon9he(file_path, join(settings.PROJECT_DIR, 'documents', 'schema', 'dtbook-2005-3-sbs-full.sch.xsl')).stderr
        if result:
            return list(result)
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
            # also check using schematron tests
            # "--validatorInputSchemas=%s" % "-//TPB//SCH dtbook 2005 Narrator//EN",
            # make sure it has to be a DTBook file
            "--validatorRequireInputType=%s" % "Dtbook document",
            # make sure files with a missing DOCTYPE declaration do
            # not validate. 
            "--validatorInputDelegates=%s" %
            "org.daisy.util.fileset.validation.delegate.impl.NoDocTypeDeclarationDelegate",
            )
        result = DaisyPipeline.replace_file_references(
            DaisyPipeline.filter_output(Popen(command, stdout=PIPE).communicate()[0].splitlines()), tmpFile)
        os.remove(tmpFile)
        return result
        
    @staticmethod
    def dtbook2pdf(inputFile, outputFile, images, **kwargs):
        """Transform a dtbook xml file to pdf"""

        tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".xml",
                                              delete=False)
        with open(inputFile) as infile, tmpFile as outfile:
            p1 = applyXSL('filterBrlContractionhints.xsl', stdin=infile, stdout=PIPE)
            p2 = applyXSL('addImageRefs.xsl', stdin=p1.stdout, stdout=outfile)
            p2.communicate()

        generatePDF(tmpFile.name, outputFile, images, **kwargs)
        os.remove(tmpFile)

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

class Pipeline2:

    @staticmethod
    def filter_output(lines):
        p = re.compile(r'^(?:\[ERROR\]|\[WS\] ERROR\([0-9]+\) -) (.*)$')
        return [p.sub(r'\1', line) for line in lines if p.match(line)]

    @staticmethod
    def dtbook2odt(inputFile, imageFiles=[], **kwargs):
        """Transform a dtbook xml file to a Open Document Format for Office Applications (ODF)"""
        
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])

        job = client2.post_job("sbs:dtbook-to-odt",
                               [inputFile],
                               [image.content.path for image in imageFiles],
                               {k.replace("_","-"): v for (k, v) in kwargs.iteritems()})

        job = client2.wait_for_job(job)

        if job['status'] == "DONE":
            try:
                odtFile = [f['href'] for f in job['results'] if f['href'].endswith(".odt")][0]
                tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".odt")
                tmpFile.close() # we are only interested in a unique filename

                with open(tmpFile.name, 'w') as file:
                    file.write(requests.get(odtFile).content)
                if not client2.delete_job(job['id']):
                    logger.warn("The job %s has not been deleted from the server", job['id'])
                return tmpFile.name
            except IndexError:
                pass

        if job:
            errors = tuple(set([m['text'] for m in job['messages'] if m['level']=='ERROR']))
            logger.error("Conversion to Open Document failed with %s. See %s", errors, job['log'])
        else:
            errors = ("Unexpected Server Response",)
        return ("Conversion to Open Document failed with:",) + errors

    @staticmethod
    def dtbook2sbsform(inputFile, imageFiles=[], **kwargs):
        """Transform a dtbook xml file to an SBSForm"""

        kwargs["version"] = getVersion()
        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])
        # map ints to strings as etree (the serializer) only wants strings
        kwargs.update([(k, str(v)) for (k, v) in kwargs.iteritems() if isinstance(v, int)])

        job = client2.post_job("sbs:dtbook-to-sbsform",
                               [inputFile],
                               [image.content.path for image in imageFiles],
                               {k.replace("_","-"): v for (k, v) in kwargs.iteritems()})
        job = client2.wait_for_job(job)

        if job['status'] == "DONE":
            try:
                sbsformFile = [f['href'] for f in job['results'] if f['href'].endswith(".sbsform")][0]
                tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".sbsform")
                tmpFile.close() # we are only interested in a unique filename

                with open(tmpFile.name, 'w') as file:
                    file.write(requests.get(sbsformFile).content)
                if not client2.delete_job(job['id']):
                    logger.warn("The job %s has not been deleted from the server", job['id'])
                return tmpFile.name
            except IndexError:
                pass

        errors = tuple(set([m['text'] for m in job['messages'] if m['level']=='ERROR']))
        logger.error("Conversion to SBSForm failed with %s. See %s", errors, job['log'])
        return ("Conversion to SBSForm failed with:",) + errors

    @staticmethod
    def dtbook2epub3(inputFile, outputPath, imageFiles=[], **kwargs):
        """Transform a dtbook xml file to an EPUB3"""

        fileName = basename(inputFile)
        epubFileName = splitext(fileName)[0] + ".epub"

        # map True and False to "true" and "false"
        kwargs.update([(k, str(v).lower()) for (k, v) in kwargs.iteritems() if isinstance(v, bool)])

        job = client2.post_job("sbs:dtbook-to-ebook",
                               [inputFile],
                               [image.content.path for image in imageFiles],
                               {k.replace("_","-"): v for (k, v) in kwargs.iteritems()})
        logger.info("Job with id %s submitted to the server", job['id'])
        job = client2.wait_for_job(job)
        if job['status'] == "DONE":
            try:
                epubFile = [f['href'] for f in job['results'] if f['href'].endswith(".epub")][0]
                tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".epub")
                tmpFile.close() # we are only interested in a unique filename

                with open(tmpFile.name, 'w') as file:
                    file.write(requests.get(epubFile).content)
                if not client2.delete_job(job['id']):
                    logger.warn("The job %s has not been deleted from the server", job['id'])
                return tmpFile.name
            except IndexError:
                pass

        errors = tuple(set([m['text'] for m in job['messages'] if m['level']=='ERROR']))
        logger.error("Conversion to EPUB3 failed with %s. See %s", errors, job['log'])
        return ("Conversion to EPUB3 failed with:",) + errors

class StandardLargePrint:

    PAGES_PER_VOLUME=200

    PARAMETER_DEFAULTS = {
        'font_size': '17pt',
        'font': 'Tiresias LPfont',
        'page_style': 'plain',
        'alignment': 'left',
        'stock_size': 'a4paper',
        'line_spacing': 'onehalfspacing',
        'paperwidth': '200mm',
        'paperheight': '250mm',
        'left_margin': '28mm',
        'right_margin': '20mm',
        'top_margin': '20mm',
        'bottom_margin': '20mm',
        'replace_em_with_quote': 'true',
        'end_notes': 'none',
        'image_visibility': 'ignore'
        }

    @staticmethod
    def insertVolumeSplitPoints(file_path, number_of_volumes):
        tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".xml", delete=False)
        tmpFile.close()
        command = (
            join(settings.DAISY_PIPELINE_PATH, 'pipeline.sh'),
            join(settings.DAISY_PIPELINE_PATH, 'scripts',
                 'modify_improve', 'dtbook', 'DTBookVolumeSplit.taskScript'),
            "--input=%s" % file_path,
            "--output=%s" % tmpFile.name,
            "--number_of_volumes=%s" % number_of_volumes,
            )
        call(command)
        return tmpFile.name

    @staticmethod
    def determineNumberOfVolumes(file_path, images, **kwargs):
        pdfFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".pdf")
        generatePDF(file_path, pdfFile.name, images, **kwargs)
        pdfReader = PdfFileReader(file(pdfFile.name, "rb"))
        volumes = int(math.ceil(pdfReader.getNumPages() / float(StandardLargePrint.PAGES_PER_VOLUME)))
        pdfFile.close()
        return volumes

    @staticmethod
    def dtbook2pdf(inputFile, outputFile, images, **kwargs):
        """Transform a dtbook xml file to pdf"""
        tmpFile = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".xml",
                                              delete=False)
        with open(inputFile) as infile, tmpFile as outfile:
            p1 = applyXSL('filterBrlContractionhints.xsl', stdin=infile, stdout=PIPE)
            p2 = applyXSL('addImageRefs.xsl', stdin=p1.stdout, stdout=outfile)
            p2.communicate()

        defaults = StandardLargePrint.PARAMETER_DEFAULTS.copy()
        defaults.update(kwargs)
        numberOfVolumes =  StandardLargePrint.determineNumberOfVolumes(tmpFile.name, images, **defaults)
        tmpFile2 = StandardLargePrint.insertVolumeSplitPoints(tmpFile.name, numberOfVolumes)

        generatePDF(tmpFile2, outputFile, images, **defaults)
        os.remove(tmpFile.name)
        os.remove(tmpFile2)

class SBSForm:

    @staticmethod
    def dtbook2sbsform(inputFile, outputFile, **kwargs):
        """Transform a dtbook xml file to sbsform"""
        hyphenate = kwargs.get('hyphenation', False)
        hyphenator = (
            "/opt/adoptium/java17/bin/java", # FIXME: this is bound to bite
            "-jar", "/usr/local/share/java/dtbook-hyphenator.jar",
            inputFile,
            )
        translator = (
            join(settings.EXTERNAL_PATH, 'dtbook2sbsform', 'dtbook2sbsform.sh'),
            "-s:-" if hyphenate else "-s:%s" % inputFile,
            )
        kwargs["version"] = getVersion()
        for k, v in kwargs.iteritems():
            if isinstance(v, bool):
                # map True and False to "true()" and "false()"
                translator += ("?%s=%s" % (k, "true()" if v else "false()"),)
            elif isinstance(v, int):
                translator += ("?%s=%s" % (k, v),)
            else:
                translator += ("%s=%s" % (k,v),)
        f = open(outputFile, 'w')
        env = {'LANG': 'en_US.UTF-8'}
        if hyphenate:
            p1 = Popen(hyphenator, stdout=PIPE, env=env)
            p2 = Popen(translator, stdin=p1.stdout, stdout=f, env=env)
        else:
            p2 = Popen(translator, stdout=f)
        p2.communicate()
        f.close()
