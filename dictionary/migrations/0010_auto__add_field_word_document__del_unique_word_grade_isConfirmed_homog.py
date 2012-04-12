# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Word', fields ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.delete_unique('dictionary_word', ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])

        # Adding field 'Word.document'
        db.add_column('dictionary_word', 'document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'], null=True, blank=True), keep_default=False)

        # Removing M2M table for field documents on 'Word'
        db.delete_table('dictionary_word_documents')

        # Adding unique constraint on 'Word', fields ['grade', 'untranslated', 'isConfirmed', 'homograph_disambiguation', 'document', 'type']
        db.create_unique('dictionary_word', ['grade', 'untranslated', 'isConfirmed', 'homograph_disambiguation', 'document_id', 'type'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Word', fields ['grade', 'untranslated', 'isConfirmed', 'homograph_disambiguation', 'document', 'type']
        db.delete_unique('dictionary_word', ['grade', 'untranslated', 'isConfirmed', 'homograph_disambiguation', 'document_id', 'type'])

        # Deleting field 'Word.document'
        db.delete_column('dictionary_word', 'document_id')

        # Adding M2M table for field documents on 'Word'
        db.create_table('dictionary_word_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('word', models.ForeignKey(orm['dictionary.word'], null=False)),
            ('document', models.ForeignKey(orm['documents.document'], null=False))
        ))
        db.create_unique('dictionary_word_documents', ['word_id', 'document_id'])

        # Adding unique constraint on 'Word', fields ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.create_unique('dictionary_word', ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dictionary.word': {
            'Meta': {'unique_together': "(('untranslated', 'type', 'grade', 'isConfirmed', 'homograph_disambiguation', 'document'),)", 'object_name': 'Word'},
            'braille': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'homograph_disambiguation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isConfirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isLocal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'untranslated': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'documents.document': {
            'Meta': {'object_name': 'Document'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {}),
            'production_series': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'production_series_number': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'production_source': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'default': "'Swiss Library for the Blind, Visually Impaired and Print Disabled'", 'max_length': '255'}),
            'rights': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'source_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'source_edition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source_publisher': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source_rights': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.State']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'documents.state': {
            'Meta': {'ordering': "['sort_order']", 'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'next_states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['documents.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'sort_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        }
    }

    complete_apps = ['dictionary']
