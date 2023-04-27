from django.urls import path

from event.views import (
    EventDetailView,
    EventListView,
    EventRegistrationDeleteView,
    EventRegistrationView,
    OrganizerDashboardView,
    OrganizerEventCreateView,
    OrganizerEventUpdateView,
)


urlpatterns = [
    path("organizer/dashboard", OrganizerDashboardView.as_view(), name="event_organizer_dashboard"),
    path("organizer/event/create", OrganizerEventCreateView.as_view(), name="event_organizer_event_create"),
    path("organizer/event/update/<int:pk>", OrganizerEventUpdateView.as_view(), name="event_organizer_event_update"),
    path("list", EventListView.as_view(), name="event_list"),
    path("detail/<int:pk>", EventDetailView.as_view(), name="event_detail"),
    path("registration/<int:pk>", EventRegistrationView.as_view(), name="event_registration"),
    path("registration/delete/<int:pk>", EventRegistrationDeleteView.as_view(), name="event_registration_delete"),
]
