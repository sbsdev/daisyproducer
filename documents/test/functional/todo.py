from daisyproducer.documents.models import Document, Version, StateError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
import django.test.client
import os

TEST_DATA_DIR= os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

# We have to do some monkey patching here since the default django
# test client encodes files always as an octet stream. However as We
# want to be able to specify the content-type we overwrite the
# default django functionality 
def get_file_encoder(content_type):
    def local_encode_file(boundary, key, file):
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
    return local_encode_file

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
        attachment = open(os.path.join(TEST_DATA_DIR, 'test.pdf'))
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
        version = open(os.path.join(TEST_DATA_DIR, 'test.xml'))
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

    def test_todo_add_version_missing_metadata(self):
        """Check if adding a version with invalid meta data fails"""
        document = Document()
        document.title = "Wachtmeister Studer"
        document.author = "Friedrich Glauser"
        document.sourcePublisher = "Diogenes"
        document.save()

        self.client.login(username='testuser', password='foobar')
        version = open(os.path.join(TEST_DATA_DIR, 'test.xml'))
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
        self.assertContains(response, "The meta data &#39;dtb:uid&#39; in the uploaded file does not correspond to the value in the document: &#39;ch-sbs-1&#39; instead of &#39;ch-sbs-")

    def test_todo_add_version(self):
        """Check if adding a version with valid mime type succeeds"""
        document = Document()
        document.title = "Wachtmeister Studer"
        document.author = "Friedrich Glauser"
        document.sourcePublisher = "Diogenes"
        document.publisher = "Swiss Library for the Blind and Visually Impaired"
        document.date = "2009-04-23"
        document.identifier = "ch-sbs-1"
        document.language = "de-CH"
        document.save()
        
        self.client.login(username='testuser', password='foobar')
        version = open(os.path.join(TEST_DATA_DIR, 'test.xml'))
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
