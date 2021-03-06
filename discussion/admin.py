from django.contrib import admin
from models import * 

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'tags', 'deleted', 'approved', 'created_at',)
    list_filter = ('approved', 'deleted',)
    list_editable = ('approved', 'deleted')
    search_fields = ('title', 'text', 'tags')
admin.site.register(Discussion, DiscussionAdmin)