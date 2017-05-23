# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20170405_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='largeprintprofile',
            name='font',
            field=models.CharField(default=b'Tiresias LPfont', max_length=60, verbose_name='Font', choices=[(b'Tiresias LPfont', b'Tiresias LPfont'), (b'Latin Modern Roman', b'Latin Modern Roman'), (b'Latin Modern Sans', b'Latin Modern Sans'), (b'Latin Modern Mono', b'Latin Modern Mono')]),
        ),
    ]
