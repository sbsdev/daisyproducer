from daisyproducer.documents.models import Document, Version
from django.core.urlresolvers import reverse
from django.test import TestCase
import os

TEST_DATA_DIR= os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))
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

    def test_manage_create_get(self):
        """Check if creation is rendered with the correct template"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('manage_create'))
        self.assertTemplateUsed(response, 'documents/manage_create.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_create_partial(self):
        """Check if creation of an invalid new document fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_create'), {
                'author': 'foo'
                })
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertFormError(response, 'form', 'language', 'This field is required.')
        self.assertTemplateUsed(response, 'documents/manage_create.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_create_invalid_language(self):
        """Check if creation of a new document with invalid language fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_create'), {
                'title': 'testing 123',
                'language': 'foo'
                })
        self.assertFormError(response, 'form', 'language', 'Select a valid choice. foo is not one of the available choices.')
        self.assertTemplateUsed(response, 'documents/manage_create.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_create(self):
        """Check if creation of a new document succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_create'), {
                'title': 'testing 123',
                'language': 'de-CH'
                })
        self.assertTemplateNotUsed(response, 'documents/manage_create.html')
        self.assertRedirects(response, reverse('manage_index'))

    def test_manage_update_get(self):
        """Check if update is rendered with the correct template"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('manage_update', args=[self.document.pk]))
        self.assertTemplateUsed(response, 'documents/manage_update.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_update_partial(self):
        """Check if update of a document with insufficient data fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_update', args=[self.document.pk]), {
                'author': 'foo'
                })
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertFormError(response, 'form', 'language', 'This field is required.')
        self.assertTemplateUsed(response, 'documents/manage_update.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_update_invalid_language(self):
        """Check if update of a document with with invalid language fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_update', args=[self.document.pk]), {
                'title': 'testing 123',
                'language': 'foo'
                })
        self.assertFormError(response, 'form', 'language', 'Select a valid choice. foo is not one of the available choices.')
        self.assertTemplateUsed(response, 'documents/manage_update.html')
        self.failUnlessEqual(response.status_code, 200)

    def test_manage_update(self):
        """Check if creation of a new document succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_update', args=[self.document.pk]), {
                'title': 'testing 456',
                'language': 'de-CH'
                })
        self.assertTemplateNotUsed(response, 'documents/manage_update.html')
        self.assertRedirects(response, reverse('manage_index'))

    def test_manage_update_with_existing_version(self):
        """Check if creation of a new document succeeds even if there is a version to update """
        from django.core.files.base import File

        document = Document()
        document.title = "Wachtmeister Studer"
        document.author = "Friedrich Glauser"
        document.sourcePublisher = "Diogenes"
        document.save()

        versionFile = File(open(os.path.join(TEST_DATA_DIR, 'test.xml')))
        version = Version.objects.create(
            comment = "testing 123",
            document = document)
        version.content.save("updated_version.xml", versionFile)
        versionFile.close()

        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('manage_update', args=[document.pk]), {
                'title': 'testing 456',
                'language': 'de-CH'
                })
        self.assertTemplateNotUsed(response, 'documents/manage_update.html')
        self.assertRedirects(response, reverse('manage_index'))

