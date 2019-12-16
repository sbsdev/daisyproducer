import datetime
import tempfile
import numbers

from django.template.loader import render_to_string
from lxml import etree
from subprocess import Popen, PIPE
from os.path import join

class XMLContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"
    XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
    ATTRIBUTE_FIELD_MAP = {
        "dc:Creator" : 'author',
        "dc:Date" : 'date',
        "dc:Description" : 'description',
        "dc:Identifier" : 'identifier',
        "dtb:uid" : 'identifier',
        "dc:Title" : 'title',
        "dc:Language" : 'language',
        "dc:Subject" : 'subject',
        "dc:Publisher" : 'publisher',
        "dc:Source" : 'source',
        "dc:Rights" : 'rights',
        "dtb:uid" : 'identifier',
        "dtb:sourceDate" : 'source_date',
        "dtb:sourcePublisher" : 'source_publisher',
        "dtb:sourceEdition" : 'source_edition',
        "dtb:sourceRights" : 'source_rights',
        "prod:series" : 'production_series',
        "prod:seriesNumber" : 'production_series_number',
        "prod:source" : 'production_source'
        }
    HUGE_TREE_PARSER = etree.XMLParser(huge_tree=True)

    @staticmethod
    def getInitialContent(document):
        from django.forms.models import model_to_dict
        dictionary = model_to_dict(document)
        dictionary['date'] = document.date.isoformat() if document.date else ''
        dictionary['source_date'] = document.source_date.isoformat() if document.source_date else ''
        content = render_to_string('DTBookTemplate.xml', dictionary)
        return content.encode('utf-8')

    @staticmethod
    def update_xml_metadata(input, output, metadata):
        """Update the meta data in given `input` file. Write the result to the
        given `output` file. Entities are not expanded."""
        command = ("java",)
        command = command + tuple(["-D%s=%s" % (key,value) for key,value in metadata.iteritems()])
        command += ("-jar", join('/usr', 'share', 'java', 'update-dtbook-metadata.jar'))
        p = Popen(command, stdin=input, stdout=output, stderr=PIPE)
        (_, error) = p.communicate()
        if p.returncode != 0:
            # the XML could not be transformed for some reason
            raise Exception(error)

    def __init__(self, version=None):
        self.version = version

    def update_version_with_metadata(self, **kwargs):
        """Update the existing version with the modified meta data"""

        # prepare meta data
        metadata = {k: v for k, v in kwargs.iteritems() if v != None and v != ''}
        metadata.update(((k, v.isoformat())) for (k, v) in metadata.iteritems() if isinstance(v, datetime.date))
        metadata.update(((k, "%s" % v)) for (k, v) in metadata.iteritems() if isinstance(v, numbers.Number))
        metadata = {k: metadata[v] for k, v in self.ATTRIBUTE_FIELD_MAP.iteritems() if v in metadata}

        with tempfile.NamedTemporaryFile(suffix='.xml', prefix='daisyproducer-') as tmpFile:
            update_xml_metadata(self.version.content.file, tmpFile, metadata)
            content = File(tmpFile)
            version = Version.objects.create(
                comment = "Updated version due to meta data change",
                document = self.version.document,
                created_by = self.user)
            version.content.save("updated_version.xml", content)

    def validateContentMetaData(self, filePath, **kwargs):
        with open(filePath) as versionFile:
            self.tree = etree.parse(versionFile, parser=self.HUGE_TREE_PARSER)
        
        validationProblems = reduce(
            # flatten the list
            lambda x,y: x+y, 
            [self._validateMetaAttribute(field, (kwargs.get(self.ATTRIBUTE_FIELD_MAP[field], '') or ''))
             for field in self.ATTRIBUTE_FIELD_MAP.keys()])

        return filter(None, validationProblems) + filter(
            None, 
            # validate language
            self._validateLangAttribute(kwargs.get('language', ''))
            )
        
    def _validateMetaAttribute(self, key, value):
        """Return a list of tuples for each meta data of name key
        where the value of the attribute 'content' doesn't match the
        given value. The tuple contains the key, the given value and
        the value of the attribute 'content'"""
        if isinstance(value, datetime.date):
            value = value.isoformat()
        r = self.tree.xpath("//dtb:meta[@name='%s']" % (key,), namespaces={'dtb': self.DTBOOK_NAMESPACE})
        if not len(r) and value != '':
            # hm the meta attribute is not there. It should be though. Report this as an error
            return [(key, '', value)]
        else:
            return [tuple([key, element.attrib['content'], value]) 
                    for element in r if element.attrib['content'] != value]
        
    def _validateLangAttribute(self, language):
        lang_attribute = self.tree.getroot().attrib['{%s}lang' % self.XML_NAMESPACE]
        return [('xml:lang', lang_attribute, language)] if lang_attribute != language else []
        
           
        
