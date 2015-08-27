# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cdbazar.migrace.models import Article
import cdbazar.store.models
import sh

class Command(BaseCommand):
    args = ""
    help = """load pictures from old cdbazar"""
    
    def handle(self, *args, **kwargs):
        self.removeAllArticles()
        Article.loadAll()

    def removeAllArticles(self):
        for obj in cdbazar.store.models.Article.objects.all():
            print "deleting article: ", obj
            obj.delete()
        
        for obj in Article.objects.all():
            obj.delete()
            print "deleting history: ", obj
