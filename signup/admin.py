from django.contrib import admin

from signup.models import EmailBasedUser, OrganizerEmail


@admin.register(OrganizerEmail)
class OrganizerEmailAdmin(admin.ModelAdmin):
    list_display = ["email"]


@admin.register(EmailBasedUser)
class EmailBasedUserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "is_organizer"]
