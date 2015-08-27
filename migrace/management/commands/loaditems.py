# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cdbazar.migrace.models import Item
import cdbazar.store.models
import sh

class Command(BaseCommand):
    args = ""
    help = """load pictures from old cdbazar"""
    
    def handle(self, *args, **kwargs):
        self.removeAllArticles()
        Article.loadAll()

    def removeAllItems(self):
        for obj in cdbazar.store.models.Item.objects.all():
            print "deleting item: ", obj
            obj.delete()
        
        for obj in Item.objects.all():
            obj.delete()
            print "deleting history: ", obj
