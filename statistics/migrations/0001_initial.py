# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DocumentStatistic'
        db.create_table('statistics_documentstatistic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('grade', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('total', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('unknown', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('statistics', ['DocumentStatistic'])


    def backwards(self, orm):
        
        # Deleting model 'DocumentStatistic'
        db.delete_table('statistics_documentstatistic')


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
        },
        'statistics.documentstatistic': {
            'Meta': {'object_name': 'DocumentStatistic'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'unknown': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['statistics']
