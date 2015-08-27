# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cdbazar.migrace.models import Picture
import cdbazar.store.models
import sh

class Command(BaseCommand):
    args = ""
    help = """load pictures from old cdbazar"""
    
    def handle(self, *args, **kwargs):
        self.removeAllPictures()
        Picture.loadAll()

    def removeAllPictures(self):
        for obj in cdbazar.store.models.Picture.objects.all():
            if obj.img.name in [ u'img/articles/empty.gif',u'img/articles/vinylempty.gif']:
                print "... skipping", obj
                continue
            
            print "deleting picture: ", obj
            obj.delete()
        
        for obj in Picture.objects.all():
            obj.delete()
            print "deleting history: ", obj
