from lxml import etree

class VersionContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"

    def __init__(self, version):
        self.version = version

    def getUpdatedContent(self, author, title, publisher, **kwargs):
        # update the existing version with the modified meta data
        self.version.content.open()
        self.tree = etree.parse(self.version.content.file)
        self.version.content.close()
        # fix author
        self.updateMetaAttribute("dc:Creator", author)
        self.updateMetaElement("docauthor", author)
        # fix title
        self.updateMetaAttribute("dc:Title", title)
        self.updateMetaElement("doctitle", title)
        # fix publisher
        self.updateMetaAttribute("dc:Publisher", publisher)
        
        return etree.tostring(self.tree, xml_declaration=True, encoding="UTF-8")

    def updateMetaAttribute(self, key, value):
        for element in self.tree.findall("//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key)):
            element.attrib['content'] = value
        
    def updateMetaElement(self, key, value):
        for element in self.tree.findall("//{%s}%s" % (self.DTBOOK_NAMESPACE, key)):
            element.text = value
        
