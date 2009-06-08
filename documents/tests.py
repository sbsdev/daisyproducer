from daisyproducer.documents.models import Document, Version
from daisyproducer.documents.versionHelper import XMLContent
from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
import os, shutil

class ManageViewTest(TestCase):
    fixtures = ['state.yaml', 'user.yaml']

    def setUp(self):
        d = Document()
        d.save()

    def test_manage_index(self):
        self.client.login(username='testuser', password='foobar')
        response = self.client.get('/manage/')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_details(self):
        self.client.login(username='testuser', password='foobar')
        response = self.client.get('/manage/1/')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_index_no_user(self):
        response = self.client.get('/manage/')
        self.failIfEqual(response.status_code, 200)

    def test_manage_details_no_user(self):
        response = self.client.get('/manage/1/')
        self.failIfEqual(response.status_code, 200)

class BrowseViewTest(TestCase):
    fixtures = ['state.yaml', 'user.yaml']

    def setUp(self):
        # clean the archive
        os.rename(settings.MEDIA_ROOT, settings.MEDIA_ROOT + '.old')
        os.mkdir(settings.MEDIA_ROOT)
        
        self.document = Document()
        self.document.save()
        contentString  = XMLContent.getInitialContent(self.document)
        content = ContentFile(contentString)
        v = Version.objects.create(
            comment = "Initial version created from meta data",
            document = self.document)
        v.content.save("initial_version.xml", content)

    def tearDown(self):
        # re-enable the archive
        shutil.rmtree(settings.MEDIA_ROOT)
        os.rename(settings.MEDIA_ROOT + '.old', settings.MEDIA_ROOT)

    def test_browse_index(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_details(self):
        response = self.client.get('/%s/' % self.document.pk)
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_pdf_empty(self):
        response = self.client.post('/%s.pdf' % self.document.pk)
        self.failIfEqual(response.status_code, 200)

    def test_browse_pdf_partial(self):
        response = self.client.post('/%s.pdf' % self.document.pk, {
                'alignment': 'justified',
                'paperSize': 'a3paper',
                })
        self.failIfEqual(response.status_code, 200)

    def test_browse_invalid(self):
        response = self.client.post('/%s.pdf' % self.document.pk, {
                'fontSize': 'foo', 
                'font': 'bar',
                'pageStyle': 'baz',
                'alignment': 'not',
                'paperSize': 'valid',
                })
        self.failIfEqual(response.status_code, 200)

    # TODO: make sure there is a version before doing this test
    def test_browse_pdf(self):
        response = self.client.post('/%s.pdf' % self.document.pk, {
                'fontSize': '14pt', 
                'font': 'Tiresias LPfont',
                'pageStyle': 'withPageNums',
                'alignment': 'justified',
                'paperSize': 'a3paper',
                })
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_brl(self):
        response = self.client.post('/%s.brl' % self.document.pk, {
                'cellsPerLine': '40', 
                'linesPerPage': '28', 
                'contraction': '0', 
                'hyphenation': '', 
                'showOriginalPageNumbers': 'True', 
                'enableCapitalization': 'True', 
                'detailedAccentedCharacters': 'True'
                })
        self.failUnlessEqual(response.status_code, 200)

    # def test_login_redirect(self):
    #     response = self.client.get('/todo', follow=True)
    #     self.assertRedirects(response, '/accounts/login', status_code=301, target_status_code=200)
