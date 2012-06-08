# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.utils.encoding import smart_unicode

class Migration(DataMigration):

    def forwards(self, orm):
        db.start_transaction()
        for word in orm.Word.objects.filter(isConfirmed=True).filter(document__isnull=True).values('untranslated', 'braille', 'grade', 'type', 'homograph_disambiguation').distinct():
            new = orm.GlobalWord(untranslated=smart_unicode(word['untranslated']), 
                                 braille=smart_unicode(word['braille']), 
                                 grade=word['grade'], type=word['type'], 
                                 homograph_disambiguation=smart_unicode(word['homograph_disambiguation']))
            new.save()
        for w in orm.Word.objects.filter(document__isnull=False):
            new = orm.LocalWord(untranslated=smart_unicode(w.untranslated), braille=smart_unicode(w.braille), 
                                grade=w.grade, type=w.type, 
                                homograph_disambiguation=smart_unicode(w.homograph_disambiguation), 
                                isLocal=w.isLocal, isConfirmed=w.isConfirmed, document=w.document)
            new.save()
        db.commit_transaction()

    def backwards(self, orm):
        db.start_transaction()
        for w in orm.GlobalWord.objects.all():
            old = orm.Word(untranslated=smart_unicode(w.untranslated), braille=smart_unicode(w.braille), 
                           grade=w.grade, type=w.type, 
                           homograph_disambiguation=smart_unicode(w.homograph_disambiguation), 
                           isLocal=False, isConfirmed=True, document=None)
            old.save()
        for w in orm.LocalWord.objects.all():
            old = orm.Word(untranslated=smart_unicode(w.untranslated), braille=smart_unicode(w.braille), 
                           grade=w.grade, type=w.type, 
                           homograph_disambiguation=smart_unicode(w.homograph_disambiguation), 
                           isLocal=w.isLocal, isConfirmed=w.isConfirmed, document=w.document)
            old.save()
        db.commit_transaction()


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
        'dictionary.globalword': {
            'Meta': {'unique_together': "(('untranslated', 'type', 'grade', 'homograph_disambiguation'),)", 'object_name': 'GlobalWord'},
            'braille': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'homograph_disambiguation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'untranslated': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'dictionary.localword': {
            'Meta': {'unique_together': "(('untranslated', 'type', 'grade', 'homograph_disambiguation', 'document'),)", 'object_name': 'LocalWord'},
            'braille': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'homograph_disambiguation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isConfirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isLocal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'untranslated': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'dictionary.word': {
            'Meta': {'unique_together': "(('untranslated', 'type', 'grade', 'homograph_disambiguation', 'document'),)", 'object_name': 'Word'},
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
