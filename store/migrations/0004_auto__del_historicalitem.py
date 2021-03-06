# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'HistoricalItem'
        db.delete_table(u'store_historicalitem')


    def backwards(self, orm):
        # Adding model 'HistoricalItem'
        db.create_table(u'store_historicalitem', (
            ('to_store', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(blank=True, max_length=128, db_index=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Article'])),
            (u'id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            ('history_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('home_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('packnumber', self.gf('django.db.models.fields.CharField')(blank=True, max_length=128, db_index=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('commentary', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=7, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'store', ['HistoricalItem'])


    models = {
        u'store.article': {
            'Meta': {'object_name': 'Article'},
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'eshop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interpret': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'mediaType': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.MediaType']", 'null': 'True', 'blank': 'True'}),
            'origPrice': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Picture']", 'null': 'True', 'blank': 'True'}),
            'pictureSource': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '126', 'null': 'True', 'blank': 'True'}),
            'specification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '222'}),
            'tracklist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'store.item': {
            'Meta': {'object_name': 'Item'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Article']"}),
            'barcode': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'commentary': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'home_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'packnumber': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'to_store': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'store.itemaction': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'ItemAction'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Item']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'store.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'})
        },
        u'store.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': "'2048'"})
        }
    }

    complete_apps = ['store']