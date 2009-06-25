from daisyproducer.documents.models import Document
from django import template
from django.core.urlresolvers import reverse
from django.test import TestCase

class TemplateTagTestCase(TestCase):

    def test_verbose_name(self):
        """Check if the verbose_name template tag works"""
        tag = """{% load verbose_name %}{{ object|verbose_name:"title" }}"""            
        response = self.client.get(reverse('browse_index'))
        t = template.Template(tag)    
        c = template.Context({'object':Document()})
        s = t.render(c)        
        self.assertEquals(s, "Title")

    def test_verbose_name(self):
        """Check if the basename template tag works"""
        tag = """{% load basename %}{{ "/foo/bar/baz.txt"|basename }}"""            
        response = self.client.get(reverse('browse_index'))
        t = template.Template(tag)    
        c = template.Context()
        s = t.render(c)        
        self.assertEquals(s, "baz.txt")
