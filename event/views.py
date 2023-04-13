from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView, UpdateView
from django.views.generic.list import ListView

from event.forms import EventForm
from event.models import Event


class OrganizerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_organizer


class OrganizerDashboardView(OrganizerMixin, ListView):
    model = Event
    fields = "__all__"
    template_name = "event/organizer/dashboard.html"

    def get_queryset(self):
        qs = Event.objects.filter(owner=self.request.user).order_by("start")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context


class OrganizerEventCreateView(OrganizerMixin, FormView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super(OrganizerEventCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse("event_organizer_dashboard")


class OrganizerEventUpdateView(OrganizerMixin, UpdateView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def get_object(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs["pk"], owner=self.request.user)
        return event

    def get_success_url(self):
        return reverse("event_organizer_dashboard")


class EventListView(ListView):
    model = Event

    def get_queryset(self):
        return Event.current_and_upcomings.filter(pub_status=Event.PubStatus.PUB)


class EventDetailView(DetailView):
    model = Event
