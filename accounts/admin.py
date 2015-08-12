# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse

from .models import (
     UserProfile
)

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile,UserProfileAdmin)
