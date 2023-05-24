from django.contrib import admin

from event.models import Booking, Contribution, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["pk", "theme", "sub_theme", "subject", "start", "pub_status"]

    search_fields = ("subject",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["pk", "event", "participant", "offer_help", "confirmed_on", "cancelled_by", "cancelled_on"]


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ["pk", "kind", "title", "public", "event"]
    search_fields = ("title",)
