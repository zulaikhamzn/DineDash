from django.contrib import admin

from dinedashapp.models import BlogPost, MenuItem, Restaurant, User

admin.site.register([User, BlogPost, Restaurant, MenuItem])
