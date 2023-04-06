from django.urls import path

from event.views import OrganizerDashboardView


urlpatterns = [
    path("organizer/dashboard", OrganizerDashboardView.as_view(), name="event_organizer_dashboard"),
]
