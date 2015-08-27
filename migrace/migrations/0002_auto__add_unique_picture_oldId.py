# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Picture', fields ['oldId']
        db.create_unique(u'migrace_picture', ['oldId'])


    def backwards(self, orm):
        # Removing unique constraint on 'Picture', fields ['oldId']
        db.delete_unique(u'migrace_picture', ['oldId'])


    models = {
        u'migrace.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oldId': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Picture']"})
        },
        u'store.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': "'2048'"})
        }
    }

    complete_apps = ['migrace']