from daisyproducer.documents.models import Document, Version
from daisyproducer.documents.versionHelper import XMLContent
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


@login_required
@permission_required("documents.add_document")
def index(request):
    response = object_list(
        request,
        queryset = Document.objects.select_related('state').all().order_by('state','title'),
        template_name = 'documents/manage_index.html',
    )
    return response
    
@login_required
@permission_required("documents.add_document")
def detail(request, document_id):
    response = object_detail(
        request,
        queryset = Document.objects.select_related('state').all(),
        template_name = 'documents/manage_detail.html',
        object_id = document_id,
    )
    return response

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'source_publisher', 'subject', 'description', 'source', 'language', 'rights', 'source_date', 'source_edition', 'source_rights', 'assigned_to')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PartialDocumentForm, self).__init__(*args, **kwargs) 

    def save(self):
        instance = super(PartialDocumentForm, self).save()
        if instance.version_set.count() == 0:
            # create an initial version
            contentString  = XMLContent.getInitialContent(instance)
            content = ContentFile(contentString)
            version = Version.objects.create(
                comment = "Initial version created from meta data",
                document = instance,
                created_by = self.user)
            version.content.save("initial_version.xml", content)
        else:
            # create a new version with the new content
            xmlContent = XMLContent(instance.latest_version())
            contentString = xmlContent.getUpdatedContent(**self.cleaned_data)
            content = ContentFile(contentString)
            version = Version.objects.create(
                comment = "Updated version due to meta data change",
                document = instance,
                created_by = self.user)
            version.content.save("updated_version.xml", content)
        return instance

@login_required
@permission_required("documents.add_document")
@transaction.commit_on_success
def create(request):
    form = PartialDocumentForm()
    if request.method == 'POST':
        form = PartialDocumentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('manage_index'))

    return render_to_response('documents/manage_create.html', locals(),
                              context_instance=RequestContext(request))

@login_required
@permission_required("documents.add_document")
@transaction.commit_on_success
def update(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    form = PartialDocumentForm(instance=document)
    if request.method == 'POST':
        form = PartialDocumentForm(request.POST,
                                   instance=document, 
                                   user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('manage_index'))

    return render_to_response('documents/manage_update.html', locals(),
                              context_instance=RequestContext(request))
