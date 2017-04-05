# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='localword',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AlterUniqueTogether(
            name='importglobalword',
            unique_together=set([('untranslated', 'type', 'grade', 'homograph_disambiguation')]),
        ),
        migrations.AlterUniqueTogether(
            name='globalword',
            unique_together=set([('untranslated', 'type', 'grade', 'homograph_disambiguation')]),
        ),
        migrations.AlterUniqueTogether(
            name='localword',
            unique_together=set([('untranslated', 'type', 'grade', 'homograph_disambiguation', 'document')]),
        ),
    ]
