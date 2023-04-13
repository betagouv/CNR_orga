from django.urls import path

from event.views import OrganizerDashboardView, OrganizerEventCreateView, OrganizerEventUpdateView


urlpatterns = [
    path("organizer/dashboard", OrganizerDashboardView.as_view(), name="event_organizer_dashboard"),
    path("organizer/event/create", OrganizerEventCreateView.as_view(), name="event_organizer_event_create"),
    path("organizer/event/update/<int:pk>", OrganizerEventUpdateView.as_view(), name="event_organizer_event_update"),
]
