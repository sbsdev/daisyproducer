# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('untranslated', models.CharField(max_length=100, verbose_name='Untranslated', db_index=True)),
                ('braille', models.CharField(max_length=100, verbose_name='Braille')),
                ('grade', models.PositiveSmallIntegerField(db_index=True, verbose_name='Grade', choices=[(1, '1'), (2, '2')])),
                ('type', models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Markup', choices=[(0, 'None'), (1, 'Name (Type Hoffmann)'), (2, 'Name'), (3, 'Place (Type Langenthal)'), (4, 'Place'), (5, 'Homograph')])),
                ('homograph_disambiguation', models.CharField(max_length=100, verbose_name='Homograph Disambiguation', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImportGlobalWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('untranslated', models.CharField(max_length=100, verbose_name='Untranslated', db_index=True)),
                ('braille', models.CharField(max_length=100, verbose_name='Braille')),
                ('grade', models.PositiveSmallIntegerField(db_index=True, verbose_name='Grade', choices=[(1, '1'), (2, '2')])),
                ('type', models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Markup', choices=[(0, 'None'), (1, 'Name (Type Hoffmann)'), (2, 'Name'), (3, 'Place (Type Langenthal)'), (4, 'Place'), (5, 'Homograph')])),
                ('homograph_disambiguation', models.CharField(max_length=100, verbose_name='Homograph Disambiguation', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocalWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('untranslated', models.CharField(max_length=100, verbose_name='Untranslated', db_index=True)),
                ('braille', models.CharField(max_length=100, verbose_name='Braille')),
                ('grade', models.PositiveSmallIntegerField(db_index=True, verbose_name='Grade', choices=[(1, '1'), (2, '2')])),
                ('type', models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='Markup', choices=[(0, 'None'), (1, 'Name (Type Hoffmann)'), (2, 'Name'), (3, 'Place (Type Langenthal)'), (4, 'Place'), (5, 'Homograph')])),
                ('homograph_disambiguation', models.CharField(max_length=100, verbose_name='Homograph Disambiguation', blank=True)),
                ('isLocal', models.BooleanField(default=False, verbose_name='Local')),
                ('isConfirmed', models.BooleanField(default=False, verbose_name='Confirmed')),
                ('isDeferred', models.BooleanField(default=False, verbose_name='Deferred')),
            ],
        ),
    ]
