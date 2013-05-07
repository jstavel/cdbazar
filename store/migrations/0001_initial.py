# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaType'
        db.create_table('store_mediatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16, db_index=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=48, blank=True)),
        ))
        db.send_create_signal('store', ['MediaType'])

        # Adding model 'Picture'
        db.create_table('store_picture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length='2048')),
        ))
        db.send_create_signal('store', ['Picture'])

        # Adding model 'Article'
        db.create_table('store_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=222)),
            ('interpret', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('mediaType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.MediaType'], null=True, blank=True)),
            ('specification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tracklist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('origPrice', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=7, decimal_places=2, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, null=True, blank=True)),
            ('pictureSource', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Picture'], null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=126, null=True, blank=True)),
            ('eshop', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('store', ['Article'])

        # Adding model 'HistoricalItem'
        db.create_table('store_historicalitem', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Article'])),
            ('commentary', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('packnumber', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=7, decimal_places=2, blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('store', ['HistoricalItem'])

        # Adding model 'Item'
        db.create_table('store_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Article'])),
            ('commentary', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('packnumber', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=7, decimal_places=2, blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('store', ['Item'])


    def backwards(self, orm):
        # Deleting model 'MediaType'
        db.delete_table('store_mediatype')

        # Deleting model 'Picture'
        db.delete_table('store_picture')

        # Deleting model 'Article'
        db.delete_table('store_article')

        # Deleting model 'HistoricalItem'
        db.delete_table('store_historicalitem')

        # Deleting model 'Item'
        db.delete_table('store_item')


    models = {
        'store.article': {
            'Meta': {'object_name': 'Article'},
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'eshop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interpret': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'mediaType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.MediaType']", 'null': 'True', 'blank': 'True'}),
            'origPrice': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.Picture']", 'null': 'True', 'blank': 'True'}),
            'pictureSource': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '126', 'null': 'True', 'blank': 'True'}),
            'specification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '222'}),
            'tracklist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'store.historicalitem': {
            'Meta': {'ordering': "('-history_id',)", 'object_name': 'HistoricalItem'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.Article']"}),
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'commentary': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'packnumber': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        'store.item': {
            'Meta': {'object_name': 'Item'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.Article']"}),
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'commentary': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'packnumber': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        'store.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'})
        },
        'store.picture': {
            'Meta': {'object_name': 'Picture'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': "'2048'"})
        }
    }

    complete_apps = ['store']