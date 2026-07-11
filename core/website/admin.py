from django.contrib import admin
from .models import ContactModel, NewsLetter


class ContactModelAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone_number", "subject", "is_seen", "created_date")


class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "created_date")


admin.site.register(ContactModel, ContactModelAdmin)
admin.site.register(NewsLetter, NewsLetterAdmin)