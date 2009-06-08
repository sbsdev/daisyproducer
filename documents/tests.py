from daisyproducer.documents.models import Document, Version, StateError
from daisyproducer.documents.versionHelper import XMLContent
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
import os, shutil

class ManageViewTest(TestCase):
    fixtures = ['state.yaml', 'user.yaml']

    def setUp(self):
        self.document = Document()
        self.document.save()

    def test_manage_index(self):
        """Check if login succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('manage_index'))
        self.assertTemplateUsed(response, 'documents/manage_index.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_details(self):
        """Check if login succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('manage_detail', args=[self.document.pk]))
        self.assertTemplateUsed(response, 'documents/manage_detail.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_index_no_user(self):
        """Check if access w/o login fails"""
        response = self.client.get(reverse('manage_index'))
        self.assertTemplateNotUsed(response, 'documents/manage_index.html')
        self.failIfEqual(response.status_code, 200)

    def test_manage_details_no_user(self):
        """Check if access w/o login fails"""
        response = self.client.get(reverse('manage_detail', args=[self.document.pk]))
        self.assertTemplateNotUsed(response, 'documents/manage_detail.html')
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
        """Check if access w/o login succeeds"""
        response = self.client.get(reverse('browse_index'))
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_details(self):
        """Check if access w/o login succeeds"""
        response = self.client.get(reverse('browse_detail', args=[self.document.pk]))
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_pdf_empty(self):
        """Check if post with an empty form fails"""
        response = self.client.post(reverse('browse_pdf', args=[self.document.pk]))
        self.failIfEqual(response.status_code, 200)

    def test_browse_pdf_partial(self):
        """Check if post with an partial form fails"""
        response = self.client.post(reverse('browse_pdf', args=[self.document.pk]), {
                'alignment': 'justified',
                'paperSize': 'a3paper',
                })
        self.failIfEqual(response.status_code, 200)

    def test_browse_pdf_invalid(self):
        """Check if post with an invalid form fails"""
        response = self.client.post(reverse('browse_pdf', args=[self.document.pk]), {
                'fontSize': 'foo', 
                'font': 'bar',
                'pageStyle': 'baz',
                'alignment': 'not',
                'paperSize': 'valid',
                })
        self.failIfEqual(response.status_code, 200)

    def test_browse_pdf(self):
        """Check if post with a valid form succeeds"""
        response = self.client.post(reverse('browse_pdf', args=[self.document.pk]), {
                'fontSize': '14pt', 
                'font': 'Tiresias LPfont',
                'pageStyle': 'withPageNums',
                'alignment': 'justified',
                'paperSize': 'a3paper',
                })
        self.failUnlessEqual(response.status_code, 200)

    def test_browse_brl_empty(self):
        """Check if post with an empty form fails"""
        response = self.client.post(reverse('browse_brl', args=[self.document.pk]))
        self.failIfEqual(response.status_code, 200)

    def test_browse_brl_partial(self):
        """Check if post with an partial form fails"""
        response = self.client.post(reverse('browse_brl', args=[self.document.pk]), {
                'cellsPerLine': '40', 
                'linesPerPage': '28', 
                })
        self.failIfEqual(response.status_code, 200)

    def test_browse_brl_invalid(self):
        """Check if post with an invalid form fails"""
        response = self.client.post(reverse('browse_brl', args=[self.document.pk]), {
                'cellsPerLine': 'foo', 
                'linesPerPage': 'bar', 
                'contraction': 'baz', 
                'hyphenation': 'not', 
                'showOriginalPageNumbers': 'even', 
                'enableCapitalization': 'remotely', 
                'detailedAccentedCharacters': 'valid'
                })
        self.failIfEqual(response.status_code, 200)

    def test_browse_brl(self):
        """Check if post with a valid form succeeds"""
        response = self.client.post(reverse('browse_brl', args=[self.document.pk]), {
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

class TodoViewTest(TestCase):
    fixtures = ['state.yaml', 'user.yaml']

    def setUp(self):
        self.document = Document()
        self.document.save()

    def test_todo_index(self):
        """Check if login succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_index'))
        self.assertTemplateUsed(response, 'documents/todo_index.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_todo_details(self):
        """Check if login succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_detail', args=[self.document.pk]))
        self.assertTemplateUsed(response, 'documents/todo_detail.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_todo_index_no_user(self):
        """Check if access w/o login fails"""
        response = self.client.get(reverse('todo_index'))
        self.assertTemplateNotUsed(response, 'documents/todo_index.html')
        self.failIfEqual(response.status_code, 200)

    def test_todo_details_no_user(self):
        """Check if access w/o login fails"""
        response = self.client.get(reverse('todo_detail', args=[self.document.pk]))
        self.assertTemplateNotUsed(response, 'documents/todo_detail.html')
        self.failIfEqual(response.status_code, 200)

    def test_todo_add_attachment(self):
        """Check if adding a valid attachment succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_add_attachment', args=[self.document.pk]), {
                'comment': 'testing 123', 
                'content': 'hah', 
                })
        self.failUnlessEqual(response.status_code, 200)

    def test_todo_transition_get(self):
        """Check if sending a get request to the transition url fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_transition', args=[self.document.pk]))
        self.failIfEqual(response.status_code, 200)

    def test_todo_transition_invalid_state(self):
        """Check if transitioning to an invalid state results in rendering the form again"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_transition', args=[self.document.pk]), 
                                    {'state': 'foo'})
        self.assertTemplateUsed(response, 'documents/todo_detail.html')

    def test_todo_transition_invalid_state(self):
        """Check if transitioning to an invalid state results in rendering the form again"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_transition', args=[self.document.pk]), 
                                    # 99 is certainly not a valid state
                                    {'state': 99})
        self.assertTemplateUsed(response, 'documents/todo_detail.html')

    def test_todo_transition_invalid_state(self):
        """Check if an invalid transition results in an StateError exception"""
        self.client.login(username='testuser', password='foobar')
        self.failUnlessRaises(StateError, 
                              self.client.post,
                              reverse('todo_transition', args=[self.document.pk]), 
                              {'state': 3})
