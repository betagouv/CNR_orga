from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView, UpdateView
from django.views.generic.list import ListView

from event.forms import EventForm, EventListFilterForm
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

    def get_theme(self):
        filter_theme = self.request.GET.get("theme", None)
        return filter_theme if filter_theme in Event.Theme.values else None

    def get_scale(self):
        filter_scale = self.request.GET.get("scale", None)
        return filter_scale if filter_scale in Event.Scale.values else None

    def get_queryset(self):
        qs = Event.current_and_upcomings.filter(pub_status=Event.PubStatus.PUB)

        filter_theme = self.get_theme()
        if filter_theme:
            qs = qs.filter(theme=filter_theme)

        filter_scale = self.get_scale()
        if filter_scale:
            qs = qs.filter(scale=filter_scale)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = EventListFilterForm(initial={"theme": self.get_theme(), "scale": self.get_scale()})
        return context


class EventDetailView(DetailView):
    model = Event
