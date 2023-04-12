from django.urls import path

from event.views import OrganizerDashboardView, OrganizerEventCreateView, OrganizerEventUpdateView


urlpatterns = [
    path("organizer/dashboard", OrganizerDashboardView.as_view(), name="event_organizer_dashboard"),
    path("organizer/event/add", OrganizerEventCreateView.as_view(), name="event_organizer_event_add"),
    path("organizer/event/edit/<int:pk>", OrganizerEventUpdateView.as_view(), name="event_organizer_event_edit"),
]
