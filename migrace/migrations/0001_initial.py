# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Picture'
        db.create_table(u'migrace_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('oldId', self.gf('django.db.models.fields.IntegerField')()),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Picture'])),
        ))
        db.send_create_signal(u'migrace', ['Picture'])


    def backwards(self, orm):
        # Deleting model 'Picture'
        db.delete_table(u'migrace_picture')


    models = {
        u'migrace.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oldId': ('django.db.models.fields.IntegerField', [], {}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Picture']"})
        },
        u'store.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': "'2048'"})
        }
    }

    complete_apps = ['migrace']