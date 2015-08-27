from django.db import models, connections
from cdbazar.settings import MEDIA_ROOT

import cdbazar.store.models
from functools import wraps

import os, sys, time, sh, re
from hashlib import md5
import magic
from operator import __not__
from itertools import chain
import django.contrib.auth.models as auth

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
        if not created:
            rel.picture=picture
            
        rel.save()
        pass

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute("select * from store_picture where id = %s", oldId)
        return Picture.loadOne(*cur.fetchone())

    @staticmethod
    @withCursorToOld
    def getOrLoadByOldId(cur, oldId):
        (rel, created) = Picture.objects.get_or_create(oldId = oldId)
        if created:
            rel.picture = Picture.loadOneByOldId(oldId)
            rel.save()
        return rel.picture


class MediaType(object):
    @staticmethod
    def get_or_create(articleType):
        return cdbazar.store.models.MediaType.objects.get_or_create(
            name=articleType, defaults = dict(desc=articleType))
    pass

class Article(models.Model):
    oldId = models.IntegerField("old article id", unique=True)
    article = models.ForeignKey(cdbazar.store.models.Article)

    @staticmethod
    @withCursorToOld
    def loadAll(cur):
        cur.execute("""select * from store_article""")
        for row in cur:
            Article.loadOne(*row)
        pass

    @staticmethod
    @withCursorToOld
    def loadOne(cur, id, title, interpret, year, 
                specification, tracklist, origPrice, ean, 
                articleType, pictureSource, group_id, picture_id,
                publisher, lastUpdate, slug):
        print "loading one article: ", id
        article = cdbazar.store.models.Article.objects.create (
            title = title,
            interpret = interpret,
            year = year,
            publisher = publisher,
            mediaType = MediaType.get_or_create(articleType),
            specification = specification,
            tracklist = tracklist,
            origPrice = origPrice,
            barcode = ean,
            pictureSource = pictureSource,
            picture = Picture.getOrLoadByOldId(picture_id),
        )
        (rel,created) = Article.objects.get_or_create(oldId = id, defaults = dict(article=article))
        if not created:
            rel.article = article
            
        rel.save()
        return article

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute("select * from store_article where id = %s", oldId)
        return Article.loadOne(*cur.fetchone())

    @staticmethod
    @withCursorToOld
    def getOrLoadByOldId(cur, oldId):
        (rel, created) = Article.objects.get_or_create(oldId = oldId)
        if created:
            rel.article = Article.loadOneByOldId(oldId)
            rel.save()
        return rel.article
        

class State(object):
    STATES = [(ii[0],ii[1].upper()) for ii in cdbazar.store.models.Item.STATES]

    @staticmethod
    def getStateId(state):
        item = [ii[0] for ii in State.STATES if ii[1] == state.upper()]
        if item:
            return item[0]
        return None

    @staticmethod
    @withCursorToOld
    def getOldUnknownStates(cur):
        cur.execute("""select distinct ws.name
        from store_item si 
        inner join workflow_instance wi on wi.id=si.workflowInstance_id 
        inner join workflow_state ws on wi.state_id = ws.id
        """)
        
        return filter(__not__(State.getStateId), chain(cur.fetchall()))

class Item(models.Model):
    oldId = models.IntegerField("old article_item id", unique=True)
    item = models.ForeignKey(cdbazar.store.models.Item)

    @staticmethod
    @withCursorToOld
    def loadAll(cur):
        cur.execute("""
        select si.*, ws.name as state 
        from store_item si 
        inner join workflow_instance wi on wi.id=si.workflowInstance_id 
        inner join workflow_state ws on wi.state_id = ws.id
        """)
        for row in cur:
            Item.loadOne(*row)
        pass

    @staticmethod
    @withCursorToOld
    def loadOne(cur, id, article_id,
                commentary, barcode, packnumber, price,
                workflowInstance_id, lastUpdated, state):
        print "loading one article item: ", id
        item = cdbazar.store.models.Item.objects.create (
            article = Article.getOrLoadByOldId(article_id),
            commentary = commentary,
            barcode = barcode,
            packnumber = packnumber,
            price = price,
            state = State.getStateId(state)
        )
        
        (rel,created) = Item.objects.get_or_create(oldId = id, defaults = dict(item=item))
        if not created:
            rel.item = item
        
        rel.save()
        return item

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute("""select si.*, ws.name as state 
        from store_item si 
        inner join workflow_instance wi on wi.id=si.workflowInstance_id 
        inner join workflow_state ws on wi.state_id = ws.id 
        where si.id = %s""", oldId)
        return Item.loadOne(*cur.fetchone())

    @staticmethod
    @withCursorToOld
    def getOrLoadByOldId(cur, oldId):
        (rel, created) = Item.objects.get_or_create(oldId = oldId)
        if created:
            rel.item = Item.loadOneByOldId(oldId)
            rel.save()
        return rel.item

class User(models.Model):
    oldId = models.IntegerField("old article_item id", unique=True)
    user = models.ForeignKey(cdbazar.store.models.Item)

    @staticmethod
    @withCursorToOld
    def loadAll(cur):
        cur.execute("""select * from auth_user where is_superuser = False""")
        for row in cur:
            User.loadOne(*row)
        pass

    @staticmethod
    @withCursorToOld
    def loadOne(cur, id, password,
                last_login, is_superuser, username, 
                first_name,last_name, email, is_staff, is_active, date_joined):
        print "loading one user: ", id
        user = auth.User.objects.create (
            password = password,
            last_login = last_login,
            is_superuser = is_superuser,
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            is_staff = is_staff,
            is_active = is_active,
            date_joined = date_joined
        )
        
        (rel,created) = User.objects.get_or_create(oldId = id, defaults = dict(user=user))
        if not created:
            rel.user = user
        
        rel.save()
        return user

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute("""select * from auth_user where id = %s""", oldId)
        return User.loadOne(*cur.fetchone())

    @staticmethod
    @withCursorToOld
    def getOrLoadByOldId(cur, oldId):
        (rel, created) = User.objects.get_or_create(oldId = oldId)
        if created:
            rel.user = User.loadOneByOldId(oldId)
            rel.save()
        return rel.user
    

class UserProfile(models.Model):
    oldId = models.IntegerField("old article_item id", unique=True)
    userProfile = models.ForeignKey(cdbazar.accounts.models.UserProfile)

    @staticmethod
    @withCursorToOld
    def loadAll(cur):
        cur.execute("""select * from registration_userprofile """)
        for row in cur:
            UserProfile.loadOne(*row)
        pass

    @staticmethod
    @withCursorToOld
    def loadOne(cur, id, user_id, individual, phone, 
                address_id, 
                correspondAddress_id, 
                firm_id, payment, delivery):
        print "loading one user profile: ", id
        userProfile = cdbazar.accounts.models.UserProfile.create (
            user = User.getOrLoadByOldId(user_id),
        )
        (rel,created) = UserProfile.objects.get_or_create(oldId = id, defaults = dict(userProfile=userProfile))
        if not created:
            rel.userProfile = userProfile
        
        rel.save()
        return userProfile

    @staticmethod
    @withCursorToOld
    def loadOneByOldId(cur, oldId):
        cur.execute(""" id = %s""", oldId)
        return UserProfile.loadOne(*cur.fetchone())

    @staticmethod
    @withCursorToOld
    def getOrLoadByOldId(cur, oldId):
        (rel, created) = UserProfile.objects.get_or_create(oldId = oldId)
        if created:
            rel.userProfile = UserProfile.loadOneByOldId(oldId)
            rel.save()
        return rel.userProfile
