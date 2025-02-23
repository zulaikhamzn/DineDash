from django.contrib import admin

from dinedashapp.models import BlogPost, User

admin.site.register([User, BlogPost])
