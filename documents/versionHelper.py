from django.template.loader import render_to_string
from lxml import etree

class XMLContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"

    @staticmethod
    def getInitialContent(author, title, publisher, **kwargs):
        content  = render_to_string('DTBookTemplate.xml', {
                'title' : title,
                'author' : author,
                'publisher' : publisher,
                })
        return content.encode('utf-8')
        
    def __init__(self, version):
        self.version = version

    def getUpdatedContent(self, author, title, publisher, **kwargs):
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
        # fix publisher
        self._updateMetaAttribute("dc:Publisher", publisher)
        
        return etree.tostring(self.tree, xml_declaration=True, encoding="UTF-8")

    def _updateMetaAttribute(self, key, value):
        for element in self.tree.findall("//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key)):
            element.attrib['content'] = value
        
    def _updateMetaElement(self, key, value):
        for element in self.tree.findall("//{%s}%s" % (self.DTBOOK_NAMESPACE, key)):
            element.text = value
        
