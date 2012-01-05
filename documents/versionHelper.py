import datetime

from django.template.loader import render_to_string
from lxml import etree


class XMLContent:
    
    DTBOOK_NAMESPACE = "http://www.daisy.org/z3986/2005/dtbook/"
    XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
    FIELD_ATTRIBUTE_MAP = {
        'subject' : "dc:Subject",
        'description' : "dc:Description",
        'publisher' : "dc:Publisher",
        'date' : "dc:Date",
        'identifier' : "dc:Identifier",
        'source' : "dc:Source",
        'language' : "dc:Language",
        'rights' : "dc:Rights",
        'identifier' : "dtb:uid",
        'source_date' : "dtb:sourceDate",
        'source_publisher': "dtb:sourcePublisher",
        'source_edition' : "dtb:sourceEdition",
        'source_rights' : "dtb:sourceRights",
        'production_series' : "prod:series",
        'production_series_number' : "prod:seriesNumber",
        'production_source' : "prod:source"
        }

    @staticmethod
    def getInitialContent(document):
        from django.forms.models import model_to_dict
        context = model_to_dict(document)
        context['date'] = document.date.isoformat() if document.date else ''
        context['source_date'] = document.source_date.isoformat() if document.source_date else ''
        content = render_to_string('DTBookTemplate.xml', context)
        return content.encode('utf-8')
        
    def __init__(self, version=None):
        self.version = version

    def getUpdatedContent(self, author, title, **kwargs):
        # update the existing version with the modified meta data
        self.version.content.open()
        self.tree = etree.parse(self.version.content.file)
        self.version.content.close()
        # fix author
        self._updateOrInsertMetaAttribute("dc:Creator", author)
        # FIXME: Sometimes the docauthor contains xml markup, such as
        # <em> and <abbr>, which is not in the meta tag. The following
        # will just wipe this out.
        self._updateMetaElement("docauthor", author)
        # fix title
        self._updateOrInsertMetaAttribute("dc:Title", title)
        # FIXME: Sometimes the doctitle contains xml markup, such as
        # <em> and <abbr>, which is not in the meta tag. The following
        # will just wipe this out.
        self._updateMetaElement("doctitle", title)
        # fix xml:lang
        self._updateLangAttribute(kwargs.get('language'))
        for model_field, field_value in kwargs.items():
            # fix attribute
            if self.FIELD_ATTRIBUTE_MAP.has_key(model_field):
                self._updateOrInsertMetaAttribute(self.FIELD_ATTRIBUTE_MAP[model_field], (field_value or ''))
       
        return etree.tostring(self.tree, xml_declaration=True, encoding="UTF-8")

    def validateContentMetaData(self, filePath, author, title, **kwargs):
        versionFile = open(filePath)
        self.tree = etree.parse(versionFile)
        versionFile.close()
        
        validationProblems = reduce(
            # flatten the list
            lambda x,y: x+y, 
            [self._validateMetaAttribute(self.FIELD_ATTRIBUTE_MAP[field], kwargs.get(field, '')) 
             for field in 
             ('source_publisher', 'subject', 'description', 'publisher', 'date', 'source', 
              'language', 'rights', 'source_date', 'source_edition', 'source_rights', 
              'production_series', 'production_series_number', 'production_source')])

        return filter(None, validationProblems) + filter(
            None, 
            # validate author
            self._validateMetaAttribute("dc:Creator", author) +
            # FIXME: It would be nice to check the docauthor element,
            # however it can contain (almost arbitrary) tags such as
            # <em>, <abbr> or any contraction hint. If we want to
            # check we need to strip the tags first.
#            self._validateMetaElement("docauthor", author) +
            # validate title
            self._validateMetaAttribute("dc:Title", title) +
            # FIXME: It would be nice to check the doctitle element,
            # however it can contain (almost arbitrary) tags such as
            # <em>, <abbr> or any contraction hint. If we want to
            # check we need to strip the tags first.
#            self._validateMetaElement("doctitle", title) +
            # validate identifier
            self._validateMetaAttribute("dc:Identifier", kwargs.get('identifier', '')) +
            self._validateMetaAttribute("dtb:uid", kwargs.get('identifier', '')) +
            # validate language
            self._validateLangAttribute(kwargs.get('language', ''))
            )
        
    def _updateOrInsertMetaAttribute(self, key, value):
        if isinstance(value, datetime.date):
            value = value.isoformat()
        elements = self.tree.findall("//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key))
        if not elements and value:
            # insert a new meta element if there wasn't one before and if the value is not empty
            head = self.tree.find("//{%s}head" % self.DTBOOK_NAMESPACE)
            etree.SubElement(head, "{%s}meta" % self.DTBOOK_NAMESPACE, name=key, content=value)
        else:
            for element in elements:
                element.attrib['content'] = value
            
        
    def _updateMetaElement(self, key, value):
        for element in self.tree.findall("//{%s}%s" % (self.DTBOOK_NAMESPACE, key)):
            element.text = value
    
    def _updateLangAttribute(self, language):
        self.tree.getroot().attrib['{%s}lang' % self.XML_NAMESPACE] = language

    def _validateMetaAttribute(self, key, value):
        """Return a list of tuples for each meta data of name key
        where the value of the attribute 'content' doesn't match the
        given value. The tuple contains the key, the given value and
        the value of the attribute 'content'"""
        if isinstance(value, datetime.date):
            value = value.isoformat()
        xpath = "//{%s}meta[@name='%s']" % (self.DTBOOK_NAMESPACE, key)
        return [tuple([key, element.attrib['content'], value]) for element in self.tree.findall(xpath) if element.attrib['content'] != value]
        
    def _validateMetaElement(self, key, value):
        """Return a list of tuples for each element of name key where
        the text doesn't match the given value. The tuple contains the
        key, the given value and the value of the text node"""
        xpath = "//{%s}%s" % (self.DTBOOK_NAMESPACE, key)
        return [tuple([key, element.text, value]) for element in self.tree.findall(xpath) if element.text != value and not (element.text == None and value == '')]

    def _validateLangAttribute(self, language):
        lang_attribute = self.tree.getroot().attrib['{%s}lang' % self.XML_NAMESPACE]
        return [('xml:lang', lang_attribute, language)] if lang_attribute != language else []
        
           
        
