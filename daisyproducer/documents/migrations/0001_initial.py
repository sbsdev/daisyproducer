# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import daisyproducer.documents.models
from django.conf import settings
import daisyproducer.documents.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=255)),
                ('mime_type', models.CharField(max_length=32, choices=[(b'application/pdf', b'Portable Document Format, PDF'), (b'application/msword', b'Microsoft Word files'), (b'application/rtf', b'Microsoft RTF files'), (b'text/html', b'HTML')])),
                ('content', models.FileField(upload_to=daisyproducer.documents.models.get_attachment_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BrailleProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cells_per_line', models.PositiveSmallIntegerField(default=40, max_length=4, verbose_name='Cells per Line')),
                ('lines_per_page', models.PositiveSmallIntegerField(default=28, max_length=4, verbose_name='Lines per Page')),
                ('contraction', models.PositiveSmallIntegerField(default=0, verbose_name='Contraction', choices=[(b'0', 'Grade 0'), (b'1', 'Grade 1'), (b'2', 'Grade 2')])),
                ('hyphenation', models.BooleanField(default=True, verbose_name='Hyphenation')),
                ('show_original_page_numbers', models.BooleanField(default=True, verbose_name='Show original page numbers')),
                ('enable_capitalization', models.BooleanField(verbose_name='Enable Capitalization')),
                ('detailed_accented_characters', models.BooleanField(verbose_name='Detailed Accented Characters')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='The title of the DTB, including any subtitles', max_length=255, verbose_name='Title')),
                ('author', models.CharField(help_text='Names of primary author or creator of the intellectual content of the publication', max_length=255, verbose_name='Author', blank=True)),
                ('subject', models.CharField(help_text='The topic of the content of the publication', max_length=255, verbose_name='Subject', blank=True)),
                ('description', models.TextField(help_text="Plain text describing the publication's content", verbose_name='Description', blank=True)),
                ('publisher', models.CharField(default=b'SBS Schweizerische Bibliothek f\xc3\xbcr Blinde, Seh- und Lesebehinderte', help_text='The agency responsible for making the DTB available', max_length=255, verbose_name='Publisher')),
                ('date', models.DateField(help_text='Date of publication of the DTB', verbose_name='Date')),
                ('identifier', models.CharField(help_text='A string or number identifying the DTB', unique=True, max_length=255, verbose_name='Identifier')),
                ('source', models.CharField(help_text='A reference to a resource (e.g., a print original, ebook, etc.) from which the DTB is derived. Best practice is to use the ISBN when available', max_length=20, verbose_name='Source', blank=True)),
                ('language', models.CharField(help_text='Language of the content of the publication', max_length=10, verbose_name='Language', choices=[(b'de', b'de'), (b'de-1901', b'de-1901'), (b'en', b'en'), (b'fr', b'fr'), (b'es', b'es')])),
                ('rights', models.CharField(help_text='Information about rights held in and over the DTB', max_length=255, verbose_name='Rights', blank=True)),
                ('source_date', models.DateField(help_text='Date of publication of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived', null=True, verbose_name='Source Date', blank=True)),
                ('source_edition', models.CharField(help_text='A string describing the edition of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived', max_length=255, verbose_name='Source Edition', blank=True)),
                ('source_publisher', models.CharField(help_text='The agency responsible for making available the resource (e.g., a print original, ebook, etc.) from which the DTB is derived', max_length=255, verbose_name='Source Publisher', blank=True)),
                ('source_rights', models.CharField(help_text='Information about rights held in and over the resource (e.g., a print original, ebook, etc.) from which the DTB is derived', max_length=255, verbose_name='Source Rights', blank=True)),
                ('production_series', models.CharField(blank=True, help_text='Information about the series under which the book is produced', max_length=25, verbose_name='Production Series', choices=[(b'SJW', b'SJW'), (b'PPP', b'Rucksack-Buch')])),
                ('production_series_number', models.CharField(help_text='Information about the number in the series under which the book is produced', max_length=25, verbose_name='Production Series Number', blank=True)),
                ('production_source', models.CharField(blank=True, help_text='Information about the source from which the book was produced, e.g. scanned book, electronic data, etc', max_length=25, verbose_name='Production Source', choices=[(b'electronicData', b'Electronic Data')])),
                ('created_at', models.DateTimeField(verbose_name='Created')),
                ('modified_at', models.DateTimeField(verbose_name='Last Modified')),
                ('assigned_to', models.ForeignKey(verbose_name='Assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.FileField(storage=daisyproducer.documents.storage.OverwriteStorage(), upload_to=daisyproducer.documents.models.get_image_path)),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'ordering': ['content'],
            },
        ),
        migrations.CreateModel(
            name='LargePrintProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('font_size', models.CharField(default=b'17pt', max_length=4, verbose_name='Fontsize', choices=[(b'12pt', b'12pt'), (b'14pt', b'14pt'), (b'17pt', b'17pt'), (b'20pt', b'20pt'), (b'25pt', b'25pt')])),
                ('font', models.CharField(default=b'Tiresias LPfont', max_length=60, verbose_name='Font', choices=[(b'Tiresias LPfont', b'Tiresias LPfont'), (b'LMRoman10 Regular', b'LMRoman10 Regular'), (b'LMSans10 Regular', b'LMSans10 Regular'), (b'LMTypewriter10 Regular', b'LMTypewriter10 Regular')])),
                ('page_style', models.CharField(default=b'plain', max_length=16, verbose_name='Page style', choices=[(b'plain', 'Plain'), (b'withPageNums', 'With original page numbers'), (b'scientific', 'Scientific')])),
                ('alignment', models.CharField(default=b'left', max_length=16, choices=[(b'justified', 'justified'), (b'left', 'left aligned')])),
                ('stock_size', models.CharField(default=b'a4paper', max_length=16, verbose_name='Stocksize', choices=[(b'a3paper', b'a3paper'), (b'a4paper', b'a4paper')])),
                ('line_spacing', models.CharField(default=b'onehalfspacing', max_length=16, verbose_name='Line Spacing', choices=[(b'singlespacing', 'Single spacing'), (b'onehalfspacing', 'One-and-a-half spacing'), (b'doublespacing', 'Double spacing')])),
                ('replace_em_with_quote', models.BooleanField(default=True, verbose_name='Replace italics with quote')),
                ('end_notes', models.CharField(default=b'none', max_length=16, verbose_name='End Notes', choices=[(b'none', 'Plain Footnotes'), (b'document', 'Document Endnotes'), (b'chapter', 'Chapter Endnotes')])),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(unique=True, max_length=255, verbose_name='Identifier')),
                ('type', models.PositiveSmallIntegerField(verbose_name='Type', choices=[(0, b'Braille'), (1, b'Large Print'), (2, b'EBook'), (3, b'E-Text')])),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('sort_order', models.PositiveSmallIntegerField()),
                ('next_states', models.ManyToManyField(to='documents.State', blank=True)),
                ('responsible', models.ManyToManyField(to='auth.Group')),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=255)),
                ('content', models.FileField(upload_to=daisyproducer.documents.models.get_version_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.AddField(
            model_name='document',
            name='state',
            field=models.ForeignKey(verbose_name='State', to='documents.State'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('document', 'content')]),
        ),
    ]
