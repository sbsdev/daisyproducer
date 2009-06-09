from daisyproducer.documents.models import Document, Version, StateError
from daisyproducer.documents.versionHelper import XMLContent
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
import django.test.client
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

def get_file_encoder(content_type):
    def encode_pdf_file(boundary, key, file):
        from django.utils.encoding import smart_str
        import os
        
        to_str = lambda s: smart_str(s, settings.DEFAULT_CHARSET)
        return [
            '--' + boundary,
            'Content-Disposition: form-data; name="%s"; filename="%s"' \
                % (to_str(key), to_str(os.path.basename(file.name))),
            'Content-Type: %s' % content_type,
            '',
            file.read()
            ]
    return encode_pdf_file

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

    def test_todo_add_attachment_get(self):
        """Check if get for adding an attachment is redirected"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_add_attachment', args=[self.document.pk]))
        self.assertRedirects(response, reverse('todo_detail', args=[self.document.pk]))

    def form_test(self, urlName, formParams, errorField):
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse(urlName, args=[self.document.pk]), formParams)
        self.assertFormError(response, 'form', errorField, 'This field is required.')

    def attachment_form_test(self, formParams, errorField):
        self.form_test('todo_add_attachment', formParams, errorField)
        
    def test_todo_add_attachment_missing_comment(self):
        """Check if adding an attachment without a comment fails"""
        self.attachment_form_test({'content': 'hah'}, 'comment')

    def test_todo_add_attachment_empty_comment(self):
        """Check if adding an attachment with an empty comment fails"""
        self.attachment_form_test({'content': '', 'content': 'hah'}, 'comment')

    def test_todo_add_attachment_missing_content(self):
        """Check if adding an attachment with no content fails"""
        self.attachment_form_test({'content': 'foo'}, 'content')

    def test_todo_add_attachment_empty_content(self):
        """Check if adding an attachment with an empty content fails"""
        self.attachment_form_test({'content': 'foo', 'content': ''}, 'content')

    def test_todo_add_attachment_invalid_mimetype(self):
        """Check if adding an attachment with wrong mime type fails"""
        self.client.login(username='testuser', password='foobar')
        attachment = open(__file__)
        post_data = {
            'comment': 'testing 123',
            'content': attachment
        }
        original_function = django.test.client.encode_file
        django.test.client.encode_file = get_file_encoder('text/plain')
        response = self.client.post(
            reverse('todo_add_attachment', args=[self.document.pk]), 
            post_data)
        attachment.close()
        django.test.client.encode_file = original_function
        self.assertFormError(response, 'form', 'content', 'The mime type of the uploaded file must be in application/pdf, application/msword, application/rtf, text/html')

    def test_todo_add_attachment_valid_mimetype(self):
        """Check if adding an attachment with valid mime type succeeds"""
        self.client.login(username='testuser', password='foobar')
        import os.path
        TEST_DIR = os.path.abspath(os.path.dirname(__file__))
        attachment = open(os.path.join(TEST_DIR, 'testdata', 'test.pdf'))
        post_data = {
            'comment': 'testing 123',
            'content': attachment, 
        }
        original_function = django.test.client.encode_file
        django.test.client.encode_file = get_file_encoder('application/pdf')
        response = self.client.post(
            reverse('todo_add_attachment', args=[self.document.pk]), 
            post_data)
        attachment.close()
        django.test.client.encode_file = original_function
        self.assertRedirects(response, reverse('todo_detail', args=[self.document.pk]))

    def test_todo_add_version_get(self):
        """Check if get for adding an version is redirected"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_add_version', args=[self.document.pk]))
        self.assertRedirects(response, reverse('todo_detail', args=[self.document.pk]))

    def version_form_test(self, formParams, errorField):
        self.form_test('todo_add_version', formParams, errorField)
        
    def test_todo_add_version_missing_comment(self):
        """Check if adding a version without a comment fails"""
        self.version_form_test({'content': 'hah'}, 'comment')

    def test_todo_add_version_empty_comment(self):
        """Check if adding a version with an empty comment fails"""
        self.version_form_test({'content': '', 'content': 'hah'}, 'comment')

    def test_todo_add_version_missing_content(self):
        """Check if adding a version with no content fails"""
        self.version_form_test({'comment': 'foo'}, 'content')

    def test_todo_add_version_empty_content(self):
        """Check if adding a version with an empty content fails"""
        self.version_form_test({'comment': 'foo', 'content': ''}, 'content')

    def test_todo_add_version(self):
        """Check if adding a valid version succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_add_version', args=[self.document.pk]), {
                'comment': 'testing 123', 
                'content': 'hah', 
                })
        self.failUnlessEqual(response.status_code, 200)

    def test_todo_add_version_invalid_mimetype(self):
        """Check if adding a version with wrong mime type fails"""
        self.client.login(username='testuser', password='foobar')
        version = open(__file__)
        post_data = {
            'comment': 'testing 123',
            'content': version
        }
        original_function = django.test.client.encode_file
        django.test.client.encode_file = get_file_encoder('text/plain')
        response = self.client.post(
            reverse('todo_add_version', args=[self.document.pk]), 
            post_data)
        version.close()
        django.test.client.encode_file = original_function
        self.assertFormError(response, 'form', 'content', "The mime type of the uploaded file must be 'text/xml'")

    def test_todo_add_version_invalid_metadata(self):
        """Check if adding a version with invalid meta data fails"""
        document = Document()
        document.title = "foo"
        document.author = "Friedrich Glauser"
        document.sourcePublisher = "Diogenes"
        document.save()

        self.client.login(username='testuser', password='foobar')
        import os.path
        TEST_DIR = os.path.abspath(os.path.dirname(__file__))
        version = open(os.path.join(TEST_DIR, 'testdata', 'test.xml'))
        post_data = {
            'comment': 'testing 123',
            'content': version, 
        }
        original_function = django.test.client.encode_file
        django.test.client.encode_file = get_file_encoder('text/xml')
        response = self.client.post(
            reverse('todo_add_version', args=[document.pk]), 
            post_data)
        version.close()
        django.test.client.encode_file = original_function
        self.assertContains(response, "The meta data &#39;dc:Title&#39; in the uploaded file does not correspond to the value in the document: &#39;Wachtmeister Studer&#39; instead of &#39;foo&#39;")

    def test_todo_add_version(self):
        """Check if adding a version with valid mime type succeeds"""
        document = Document()
        document.title = "Wachtmeister Studer"
        document.author = "Friedrich Glauser"
        document.sourcePublisher = "Diogenes"
        document.save()

        self.client.login(username='testuser', password='foobar')
        import os.path
        TEST_DIR = os.path.abspath(os.path.dirname(__file__))
        version = open(os.path.join(TEST_DIR, 'testdata', 'test.xml'))
        post_data = {
            'comment': 'testing 123',
            'content': version, 
        }
        original_function = django.test.client.encode_file
        django.test.client.encode_file = get_file_encoder('text/xml')
        response = self.client.post(
            reverse('todo_add_version', args=[document.pk]), 
            post_data)
        version.close()
        django.test.client.encode_file = original_function
        self.assertRedirects(response, reverse('todo_detail', args=[document.pk]))

    def test_todo_transition_get(self):
        """Check if sending a get request to the transition url fails"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.get(reverse('todo_transition', args=[self.document.pk]))
        self.failIfEqual(response.status_code, 200)

    def transition_test(self, formParams, errorMsg):
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_transition', args=[self.document.pk]), formParams)
        self.assertFormError(response, 'form', 'state', errorMsg)
        self.assertTemplateUsed(response, 'documents/todo_detail.html')

    def test_todo_transition_no_state(self):
        """Check if transitioning to no state results in a form error"""
        self.transition_test({}, 'This field is required.')

    def test_todo_transition_invalid_state(self):
        """Check if transitioning to an invalid state results in rendering the form again"""
        self.transition_test({'state': 'foo'}, 
                             'Select a valid choice. foo is not one of the available choices.')

    def test_todo_transition_invalid_state(self):
        """Check if transitioning to an invalid state results in rendering the form again"""
        # 99 is certainly not a valid state
        self.transition_test({'state': 99}, 
                             'Select a valid choice. 99 is not one of the available choices.')

    def test_todo_transition_invalid_state(self):
        """Check if an invalid transition results in an StateError exception"""
        self.client.login(username='testuser', password='foobar')
        self.failUnlessRaises(StateError, 
                              self.client.post,
                              reverse('todo_transition', args=[self.document.pk]), 
                              {'state': 3})

    def test_todo_transition_valid_state(self):
        """Check if an valid transition succeeds"""
        self.client.login(username='testuser', password='foobar')
        response = self.client.post(reverse('todo_transition', args=[self.document.pk]), 
                                    {'state': 2})
        self.assertRedirects(response, reverse('todo_index'))
