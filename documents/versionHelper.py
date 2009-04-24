from daisyproducer import settings
from datetime import date
from django.template.loader import render_to_string
from lxml import etree

class XMLContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"

    @staticmethod
    def getInitialContent(document):
        content  = render_to_string('DTBookTemplate.xml', {
                'title' : document.title,
                'author' : document.author,
                'publisher' : settings.DAISY_DEFAULT_PUBLISHER,
                'date' : date.today().isoformat(),
                'identifier' : "ch-sbs-%s" % document.id,
                'language' : "de-CH",
                'sourcePublisher' : document.sourcePublisher
                })
        return content.encode('utf-8')
        
    def __init__(self, version=None):
        self.version = version

    def getUpdatedContent(self, author, title, sourcePublisher, **kwargs):
        # update the existing version with the modified meta data
        self.version.content.open()
        self.tree = etree.parse(self.version.content.file)
        self.version.content.close()
        # fix author
        self._updateMetaAttribute("dc:Creator", author)
        self._updateMetaElement("docauthor", author)
        # fix title
        self._updateMetaAttribute("dc:Title", title)
        self._updateMetaElement("doctitle", title)
        # fix sourcePublisher
        self._updateMetaAttribute("dtb:sourcePublisher", sourcePublisher)
        
        return etree.tostring(self.tree, xml_declaration=True, encoding="UTF-8")

    def validateContentMetaData(self, filePath, author, title, sourcePublisher, **kwargs):
        versionFile = open(filePath)
        self.tree = etree.parse(versionFile)
        versionFile.close()
        
        return filter(
            None, 
            # validate author
            self._validateMetaAttribute("dc:Creator", author) +
            self._validateMetaElement("docauthor", author) +
            # validate title
            self._validateMetaAttribute("dc:Title", title) +
            self._validateMetaElement("doctitle", title) +
            # validate sourcePublisher
            self._validateMetaAttribute("dtb:sourcePublisher", sourcePublisher)
            )
        
    def _updateMetaAttribute(self, key, value):
        for element in self.tree.findall("//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key)):
            element.attrib['content'] = value
        
    def _updateMetaElement(self, key, value):
        for element in self.tree.findall("//{%s}%s" % (self.DTBOOK_NAMESPACE, key)):
            element.text = value
        
    def _validateMetaAttribute(self, key, value):
        """Return a list of tuples for each meta data of name key
        where the value of the attribute 'content' doesn't match the
        given value. The tuple contains the key, the given value and
        the value of the attribute 'content'"""
        xpath = "//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key)
        return [tuple([key, element.attrib['content'], value]) for element in self.tree.findall(xpath) if element.attrib['content'] != value]
        
    def _validateMetaElement(self, key, value):
        """Return a list of tuples for each element of name key where
        the text doesn't match the given value. The tuple contains the
        key, the given value and the value of the text node"""
        xpath = "//{%s}%s" % (self.DTBOOK_NAMESPACE, key)
        return [tuple([key, element.text, value]) for element in self.tree.findall(xpath) if element.text != value]
           
        
