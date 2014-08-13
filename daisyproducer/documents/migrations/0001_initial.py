# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'State'
        db.create_table('documents_state', (
            ('sort_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('documents', ['State'])

        # Adding M2M table for field responsible on 'State'
        db.create_table('documents_state_responsible', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('state', models.ForeignKey(orm['documents.state'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('documents_state_responsible', ['state_id', 'group_id'])

        # Adding M2M table for field next_states on 'State'
        db.create_table('documents_state_next_states', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_state', models.ForeignKey(orm['documents.state'], null=False)),
            ('to_state', models.ForeignKey(orm['documents.state'], null=False))
        ))
        db.create_unique('documents_state_next_states', ['from_state_id', 'to_state_id'])

        # Adding model 'Document'
        db.create_table('documents_document', (
            ('publisher', self.gf('django.db.models.fields.CharField')(default='Swiss Library for the Blind, Visually Impaired and Print Disabled', max_length=255)),
            ('production_series', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('rights', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source_rights', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('production_series_number', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('source_publisher', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.State'])),
            ('source_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('source_edition', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('documents', ['Document'])

        # Adding model 'Version'
        db.create_table('documents_version', (
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('documents', ['Version'])

        # Adding model 'Attachment'
        db.create_table('documents_attachment', (
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('documents', ['Attachment'])

        # Adding model 'BrailleProfile'
        db.create_table('documents_brailleprofile', (
            ('cells_per_line', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=40, max_length=4)),
            ('detailed_accented_characters', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('show_original_page_numbers', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('lines_per_page', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=28, max_length=4)),
            ('enable_capitalization', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('hyphenation', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contraction', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('documents', ['BrailleProfile'])

        # Adding model 'LargePrintProfile'
        db.create_table('documents_largeprintprofile', (
            ('page_style', self.gf('django.db.models.fields.CharField')(default='plain', max_length=16)),
            ('font_size', self.gf('django.db.models.fields.CharField')(default='17pt', max_length=4)),
            ('line_spacing', self.gf('django.db.models.fields.CharField')(default='singlespacing', max_length=16)),
            ('paper_size', self.gf('django.db.models.fields.CharField')(default='a4paper', max_length=16)),
            ('replace_em_with_quote', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('font', self.gf('django.db.models.fields.CharField')(default='Tiresias LPfont', max_length=60)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alignment', self.gf('django.db.models.fields.CharField')(default='justified', max_length=16)),
        ))
        db.send_create_signal('documents', ['LargePrintProfile'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'State'
        db.delete_table('documents_state')

        # Removing M2M table for field responsible on 'State'
        db.delete_table('documents_state_responsible')

        # Removing M2M table for field next_states on 'State'
        db.delete_table('documents_state_next_states')

        # Deleting model 'Document'
        db.delete_table('documents_document')

        # Deleting model 'Version'
        db.delete_table('documents_version')

        # Deleting model 'Attachment'
        db.delete_table('documents_attachment')

        # Deleting model 'BrailleProfile'
        db.delete_table('documents_brailleprofile')

        # Deleting model 'LargePrintProfile'
        db.delete_table('documents_largeprintprofile')
    
    
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
        'documents.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'documents.brailleprofile': {
            'Meta': {'object_name': 'BrailleProfile'},
            'cells_per_line': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '40', 'max_length': '4'}),
            'contraction': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'detailed_accented_characters': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_capitalization': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'hyphenation': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines_per_page': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '28', 'max_length': '4'}),
            'show_original_page_numbers': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
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
        'documents.largeprintprofile': {
            'Meta': {'object_name': 'LargePrintProfile'},
            'alignment': ('django.db.models.fields.CharField', [], {'default': "'justified'", 'max_length': '16'}),
            'font': ('django.db.models.fields.CharField', [], {'default': "'Tiresias LPfont'", 'max_length': '60'}),
            'font_size': ('django.db.models.fields.CharField', [], {'default': "'17pt'", 'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_spacing': ('django.db.models.fields.CharField', [], {'default': "'singlespacing'", 'max_length': '16'}),
            'page_style': ('django.db.models.fields.CharField', [], {'default': "'plain'", 'max_length': '16'}),
            'paper_size': ('django.db.models.fields.CharField', [], {'default': "'a4paper'", 'max_length': '16'}),
            'replace_em_with_quote': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'documents.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'next_states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['documents.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'sort_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'documents.version': {
            'Meta': {'object_name': 'Version'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['documents']
