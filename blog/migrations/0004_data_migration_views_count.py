# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-08 10:06

from django.db import migrations
from django.conf import settings
from datetime import datetime
from blog.utils import get_default_views_count


def set_views_count(apps, schema_editor):
    Blog = apps.get_model('blog', 'Blog')
    for blog in Blog.objects.all():
        days_old = (datetime.now() - blog.create_time.replace(tzinfo=None)).days
        min_views = 300 + (days_old / 4)
        max_views = 500 + days_old
        blog.views_count = get_default_views_count(min_views, max_views)
        blog.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blog_views_count'),
    ]

    operations = [
        migrations.RunPython(set_views_count),
    ]
