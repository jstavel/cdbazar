from django.db import models, connections
from cdbazar.settings import MEDIA_ROOT

import cdbazar.store.models
from functools import wraps

import os, sys, time, sh, re
from hashlib import md5
import magic

def withCursorToOld(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        cur = connections['old'].cursor()
        result = f(cur,*args,**kwargs)
        return result
    
    return wrapper

old_cdbazar_path = '/srv/www/cdbazar'

class Picture(models.Model):
    oldId = models.IntegerField("old picture id", unique=True)
    picture = models.ForeignKey(cdbazar.store.models.Picture)

    @staticmethod
    @withCursorToOld
    def loadAll(cur):
        cur.execute("select * from store_picture limit 10")
        for row in cur:
            Picture.loadOne(*row)
        pass

    @staticmethod
    @withCursorToOld
    def loadOne(cur, id, img):
        print "loading one picture: ", id
        oldImgPath = old_cdbazar_path + "/media/" + img
        picture = cdbazar.store.models.Picture.loadFromFile(oldImgPath)
        (rel,created) = Picture.objects.get_or_create(oldId = id, defaults = dict(picture=picture))
        if created:
            print "... picture is new, saving"
            rel.save()
        pass

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute("select * from store_picture where id = %s", oldId)
        return Picture.loadOne(cur.fetchone())
        
        
