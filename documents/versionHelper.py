from datetime import date
from django.template.loader import render_to_string
from lxml import etree
import datetime

class XMLContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"
    FIELD_ATTRIBUTE_MAP = {
            'subject' : "dtb:Subject",
             'description' : "dtb:Description",
             'publisher' : "dtb:Publisher",
             'date' : "dtb:Date",
             'identifier' : "dtb:Identifier",
             'source' : "dtb:Source",
             'language' : "dtb:Language",
             'rights' : "dtb:Rights",
             'identifier' : "dtb:uid",
             'sourceDate' : "dtb:sourceDate",
             'sourceEdition' : "dtb:sourceEdition",
             'sourceRights' : "dtb:sourceRights"
        }

    @staticmethod
    def getInitialContent(document):
        from django.forms.models import model_to_dict
        context = model_to_dict(document)
        context['date'] = document.date.isoformat() if document.date else ''
        context['sourceDate'] = document.sourceDate.isoformat() if document.sourceDate else ''
        content = render_to_string('DTBookTemplate.xml', context)
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
        for model_field, field_value in kwargs.items():
            # fix attribute
            if self.FIELD_ATTRIBUTE_MAP.has_key(model_field):
                self._updateMetaAttribute(self.FIELD_ATTRIBUTE_MAP[model_field], (field_value or ''))
       
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
            self._validateMetaAttribute("dtb:sourcePublisher", sourcePublisher) +
            # validate subject
            self._validateMetaAttribute("dtb:Subject", kwargs.get('subject', '')) +
            # validate description
            self._validateMetaAttribute("dtb:Description", kwargs.get('description', '')) +
            # validate publisher
            self._validateMetaAttribute("dtb:Publisher", kwargs.get('publisher', '')) +
            # validate date
            self._validateMetaAttribute("dtb:Date", (kwargs.get('date') or '')) +
            # validate identifier
            self._validateMetaAttribute("dtb:Identifier", kwargs.get('identifier', '')) +
            # validate source
            self._validateMetaAttribute("dtb:Source", kwargs.get('source', '')) +
            # validate language
            self._validateMetaAttribute("dtb:Language", kwargs.get('language', '')) +
            # validate rights
            self._validateMetaAttribute("dtb:Rights", kwargs.get('rights', '')) +
            # validate identifier
            self._validateMetaAttribute("dtb:uid", kwargs.get('identifier', '')) +
            # validate sourceDate
            self._validateMetaAttribute("dtb:sourceDate", (kwargs.get('sourceDate') or '')) +
            # validate sourceEdition
            self._validateMetaAttribute("dtb:sourceEdition", kwargs.get('sourceEdition', '')) +
            # validate sourceRights
            self._validateMetaAttribute("dtb:sourceRights", kwargs.get('sourceRights', ''))
            )
        
    def _updateMetaAttribute(self, key, value):
        if isinstance(value, datetime.date):
            value = value.isoformat()
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
           
        
