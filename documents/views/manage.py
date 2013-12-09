import csv, codecs, re

from daisyproducer.documents.forms import CSVUploadForm, PartialProductForm
from daisyproducer.documents.models import Document, Version, Product
from daisyproducer.documents.versionHelper import XMLContent
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

VALID_ISBN_RE = re.compile(u"^[0-9-X]{10,18}$")

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
        fields = ('title', 'author', 'source_publisher', 'subject', 'description', 'source', 'language', 'rights', 'source_date', 'source_edition', 'source_rights', 'production_series', 'production_series_number', 'production_source', 'assigned_to',)

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

# The following two classes are from http://docs.python.org/release/2.6.5/library/csv.html
class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

@login_required
@permission_required("documents.add_document")
@transaction.commit_on_success
def upload_metadata_csv(request):

    if request.method != 'POST':
        form = CSVUploadForm()
        return render_to_response('documents/manage_upload_metadata_csv.html', locals(), 
                                  context_instance=RequestContext(request))

    form = CSVUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render_to_response('documents/manage_upload_metadata_csv.html', locals(), 
                                  context_instance=RequestContext(request))
            
    csv_file = request.FILES['csv']
    # FIXME: It's pretty annoying to hard code the expected encoding of the csv
    reader = UnicodeReader(open(csv_file.temporary_file_path()), encoding="iso-8859-1", delimiter='\t')
    initial = []
    products = {}
    seen_sources = set()
    seen_title_author = set()
    for row in reader:
        fields = {'title': row[0], 'author': row[1], 
                  'identifier': row[2], 'source': row[3], 
                  'source_edition': row[4], 'source_publisher': row[5],
                  'language': Document.language_choices[0][0]}
        # collect all products for a given isbn
        if fields['source'] != '' and VALID_ISBN_RE.match(fields['source']):
            products.setdefault(fields['source'], set()).add(fields['identifier'])
        # filter entries in the csv that deal with the same isbn or with the same title/author combo
        if fields['source'] in seen_sources or fields['title'] + fields['author'] in seen_title_author:
            continue
        if fields['source']:
            seen_sources.add(fields['source'])
        if fields['title'] + fields['author']:
            seen_title_author.add(fields['title'] + fields['author'])
        # FIXME: Obviously the following is highly SBS specific
        if row[7] != '0':
            fields['production_series'] = Document.PRODUCTION_SERIES_CHOICES[1][0]
            fields['production_series_number'] = row[7]
        elif row[6].upper().find('SJW') != -1:
            fields['production_series'] = Document.PRODUCTION_SERIES_CHOICES[0][0]
            m = re.search('\d+', row[6]) # extract the series number
            if m != None:
                fields['production_series_number'] = m.group(0)
        if row[8] == 'D':
            fields['production_source'] = Document.PRODUCTION_SOURCE_CHOICES[0][0]
        initial.append(fields)
    # filter out existing document entries
    new_identifiers = [row['identifier'] for row in initial]
    new_sources = [row['source'] for row in initial if row['source']]
    duplicate_identifiers = [document.identifier for 
                             document in Document.objects.filter(identifier__in=new_identifiers)]
    duplicate_sources = [document.source for 
                         document in Document.objects.filter(source__in=new_sources)]
    unique_initial = [row for row in initial if row['identifier'] not in duplicate_identifiers and row['source'] not in duplicate_sources]
    ProductFormset = formset_factory(PartialProductForm, extra=0)
    product_formset = ProductFormset(initial=[{'isbn': isbn, 'productNumber': number} for (isbn, v) in products.items() for number in v],
                                     prefix='products')
    DocumentFormSet = modelformset_factory(Document, 
                                           fields=('author', 'title', 'identifier', 'source', 'source_edition', 'source_publisher', 'language', 'production_series', 'production_series_number', 'production_source'), 
                                           extra=len(unique_initial), can_delete=True)
    document_formset = DocumentFormSet(queryset=Document.objects.none(), initial=unique_initial, prefix='documents')
    return render_to_response('documents/manage_import_metadata_csv.html', locals(),
                              context_instance=RequestContext(request))

@login_required
@permission_required("documents.add_document")
@transaction.commit_on_success
def import_metadata_csv(request):

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('upload_metadata_csv'))

    DocumentFormSet = modelformset_factory(Document, 
                                           fields=('author', 'title', 'identifier', 'source', 'source_edition', 'source_publisher', 'language', 'production_series', 'production_series_number', 'production_source'), 
                                           can_delete=True)
    ProductFormset = formset_factory(PartialProductForm)
    document_formset = DocumentFormSet(request.POST, prefix='documents')
    product_formset = ProductFormset(request.POST, prefix='products')
    if not document_formset.is_valid() or not product_formset.is_valid():
        return render_to_response('documents/manage_import_metadata_csv.html', locals(),
                                  context_instance=RequestContext(request))
    instances = document_formset.save()
    for instance in instances:
        if instance.version_set.count() == 0:
            # create an initial version
            contentString  = XMLContent.getInitialContent(instance)
            content = ContentFile(contentString)
            version = Version.objects.create(
                comment = "Initial version created from meta data",
                document = instance,
                created_by = request.user)
            version.content.save("initial_version.xml", content)
    products = {}
    for form in product_formset.forms:
        isbn, product_number = form.cleaned_data['isbn'], form.cleaned_data['productNumber']
        products.setdefault(isbn, set()).add(product_number)
    for document in Document.objects.filter(source__in=products.keys()):
        for product_number in products[document.source]:
            if product_number.startswith('PS'):
                type = 0
            elif product_number.startswith('GD'):
                type = 1
            elif product_number.startswith('EB'):
                type = 2
            elif product_number.startswith('ET'):
                type = 3
            else:
                continue
            Product.objects.get_or_create(document=document, type=type, identifier=product_number)
    return HttpResponseRedirect(reverse('manage_index'))
