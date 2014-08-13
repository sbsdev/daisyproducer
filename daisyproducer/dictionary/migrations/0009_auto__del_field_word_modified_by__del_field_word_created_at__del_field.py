# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Word.modified_by'
        db.delete_column('dictionary_word', 'modified_by_id')

        # Deleting field 'Word.created_at'
        db.delete_column('dictionary_word', 'created_at')

        # Deleting field 'Word.modified_at'
        db.delete_column('dictionary_word', 'modified_at')

        # Deleting field 'Word.grade1'
        db.delete_column('dictionary_word', 'grade1')

        # Deleting field 'Word.grade2'
        db.delete_column('dictionary_word', 'grade2')

        # Deleting field 'Word.use_for_word_splitting'
        db.delete_column('dictionary_word', 'use_for_word_splitting')

        # Adding field 'Word.braille'
        db.add_column('dictionary_word', 'braille', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Word.grade'
        db.add_column('dictionary_word', 'grade', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=2, db_index=True), keep_default=False)

        # Changing field 'Word.untranslated'
        db.alter_column('dictionary_word', 'untranslated', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Word.homograph_disambiguation'
        db.alter_column('dictionary_word', 'homograph_disambiguation', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True))

        # Removing unique constraint on 'Word', fields ['isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.delete_unique('dictionary_word', ['isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])

        # Adding unique constraint on 'Word', fields ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.create_unique('dictionary_word', ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])
    
    
    def backwards(self, orm):
        
        # Adding field 'Word.modified_by'
        db.add_column('dictionary_word', 'modified_by', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['auth.User']), keep_default=False)

        # Adding field 'Word.created_at'
        db.add_column('dictionary_word', 'created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 2, 24, 10, 46, 25, 942822)), keep_default=False)

        # Adding field 'Word.modified_at'
        db.add_column('dictionary_word', 'modified_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 2, 24, 10, 46, 38, 352776)), keep_default=False)

        # Adding field 'Word.grade1'
        db.add_column('dictionary_word', 'grade1', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)

        # Adding field 'Word.grade2'
        db.add_column('dictionary_word', 'grade2', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)

        # Adding field 'Word.use_for_word_splitting'
        db.add_column('dictionary_word', 'use_for_word_splitting', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True), keep_default=False)

        # Deleting field 'Word.braille'
        db.delete_column('dictionary_word', 'braille')

        # Deleting field 'Word.grade'
        db.delete_column('dictionary_word', 'grade')

        # Changing field 'Word.untranslated'
        db.alter_column('dictionary_word', 'untranslated', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Word.homograph_disambiguation'
        db.alter_column('dictionary_word', 'homograph_disambiguation', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True))

        # Adding unique constraint on 'Word', fields ['isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.create_unique('dictionary_word', ['isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])

        # Removing unique constraint on 'Word', fields ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type']
        db.delete_unique('dictionary_word', ['grade', 'isConfirmed', 'homograph_disambiguation', 'untranslated', 'type'])
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dictionary.word': {
            'Meta': {'unique_together': "(('untranslated', 'type', 'grade', 'isConfirmed', 'homograph_disambiguation'),)", 'object_name': 'Word'},
            'braille': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'homograph_disambiguation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isConfirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'isLocal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'next_states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['documents.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'sort_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        }
    }
    
    complete_apps = ['dictionary']
