# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brailleprofile',
            name='cells_per_line',
            field=models.PositiveSmallIntegerField(default=40, verbose_name='Cells per Line'),
        ),
        migrations.AlterField(
            model_name='brailleprofile',
            name='detailed_accented_characters',
            field=models.BooleanField(default=False, verbose_name='Detailed Accented Characters'),
        ),
        migrations.AlterField(
            model_name='brailleprofile',
            name='enable_capitalization',
            field=models.BooleanField(default=False, verbose_name='Enable Capitalization'),
        ),
        migrations.AlterField(
            model_name='brailleprofile',
            name='lines_per_page',
            field=models.PositiveSmallIntegerField(default=28, verbose_name='Lines per Page'),
        ),
    ]
