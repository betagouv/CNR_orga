from django.urls import path

from event.views import (
    ContributionCreateView,
    ContributionUpdateView,
    EventDetailView,
    EventListView,
    EventRegistrationDeleteView,
    EventRegistrationView,
    OrganizerDashboardView,
    OrganizerEventCreateView,
    OrganizerEventDetailView,
    OrganizerEventUpdateView,
    OrganizerRegistrationAcceptView,
    OrganizerRegistrationDeclineView,
)


urlpatterns = [
    # Organizer
    path("organizer/dashboard", OrganizerDashboardView.as_view(), name="event_organizer_dashboard"),
    path("organizer/event/create", OrganizerEventCreateView.as_view(), name="event_organizer_event_create"),
    path("organizer/event/<int:pk>/detail/", OrganizerEventDetailView.as_view(), name="event_organizer_event_detail"),
    path("organizer/event/<int:pk>/update/", OrganizerEventUpdateView.as_view(), name="event_organizer_event_update"),
    path(
        "organizer/registration/<int:pk>/accept/",
        OrganizerRegistrationAcceptView.as_view(),
        name="event_organizer_registration_accept",
    ),
    path(
        "organizer/registration/<int:pk>/decline/",
        OrganizerRegistrationDeclineView.as_view(),
        name="event_organizer_registration_decline",
    ),
    path(
        "organizer/event/<int:event_pk>/contribution/create",
        ContributionCreateView.as_view(),
        name="event_organizer_contribution_create",
    ),
    path(
        "organizer/contribution/<int:pk>/update",
        ContributionUpdateView.as_view(),
        name="event_organizer_contribution_update",
    ),
    # Participant
    path("list", EventListView.as_view(), name="event_list"),
    path("detail/<int:pk>", EventDetailView.as_view(), name="event_detail"),
    path("registration/<int:pk>", EventRegistrationView.as_view(), name="event_registration"),
    path("registration/delete/<int:pk>", EventRegistrationDeleteView.as_view(), name="event_registration_delete"),
]
