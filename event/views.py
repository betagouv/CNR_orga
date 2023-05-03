from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from event.forms import EventForm, EventListFilterForm, EventRegistrationForm
from event.models import Booking, Event


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


class OrganizerEventCreateView(OrganizerMixin, FormView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super(OrganizerEventCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("event_organizer_dashboard")


class OrganizerEventDetailView(OrganizerMixin, DetailView):
    template_name = "event/organizer/event_detail.html"
    model = Event

    def get_object(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs["pk"], owner=self.request.user)
        return event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings"] = Booking.objects.filter(event=self.object)
        return context


class OrganizerEventUpdateView(OrganizerMixin, UpdateView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Event, pk=self.kwargs["pk"], owner=self.request.user)

    def get_success_url(self):
        return reverse("event_organizer_event_detail", kwargs={"pk": self.object.pk})


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["booking"] = Booking.objects.filter(event=self.object, participant=self.request.user).first()
        return context


class EventRegistrationView(LoginRequiredMixin, FormView):
    template_name = "event/event_registration.html"
    form_class = EventRegistrationForm

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs.get("pk"))

    def form_valid(self, form):
        form.instance.event = self.get_event()
        form.instance.participant = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

    def get_success_url(self):
        return reverse("event_detail", kwargs={"pk": self.kwargs.get("pk")})


class EventRegistrationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking

    # test if booking is owned by correct user
    def test_func(self):
        booking = get_object_or_404(Booking, pk=self.kwargs.get("pk"), participant=self.request.user)
        return booking is not None

    def get_success_url(self):
        return reverse("event_detail", kwargs={"pk": self.object.event.pk})
