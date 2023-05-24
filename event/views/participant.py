from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from event.forms import ContributionListFilterForm, EventListFilterForm, EventRegistrationForm
from event.models import Booking, Contribution, Event


class EventListView(ListView):
    model = Event

    def get_theme(self):
        filter_theme = self.request.GET.get("theme", None)
        return filter_theme if filter_theme in Event.Theme.values else None

    def get_scale(self):
        filter_scale = self.request.GET.get("scale", None)
        return filter_scale if filter_scale in Event.Scale.values else None

    def get_upcoming(self):
        return self.request.GET.get("upcoming", None) == "on"

    def get_queryset(self):
        if self.get_upcoming():
            qs = Event.current_and_upcomings.filter(pub_status=Event.PubStatus.PUB)
        else:
            qs = Event.objects.filter(pub_status=Event.PubStatus.PUB)

        filter_theme = self.get_theme()
        if filter_theme:
            qs = qs.filter(theme=filter_theme)

        filter_scale = self.get_scale()
        if filter_scale:
            qs = qs.filter(scale=filter_scale)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = EventListFilterForm(
            initial={"theme": self.get_theme(), "scale": self.get_scale(), "upcoming": self.get_upcoming()}
        )
        context["current_page_event_list"] = True
        return context


class EventDetailView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["booking"] = Booking.objects.filter(event=self.object, participant=self.request.user).first()

        context["contributions"] = Contribution.objects.filter(event=self.object, public=True)
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


class ContributionListView(ListView):
    model = Contribution
    paginate_by = 4

    def get_theme(self):
        filter_theme = self.request.GET.get("theme", None)
        return filter_theme if filter_theme in Event.Theme.values else None

    # TODO : set tags filter

    def get_scale(self):
        filter_scale = self.request.GET.get("scale", None)
        return filter_scale if filter_scale in Event.Scale.values else None

    def get_queryset(self):
        qs = Contribution.objects.filter(event__pub_status=Event.PubStatus.PUB)

        filter_theme = self.get_theme()
        if filter_theme:
            qs = qs.filter(event__theme=filter_theme)

        filter_scale = self.get_scale()
        if filter_scale:
            qs = qs.filter(event__scale=filter_scale)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = ContributionListFilterForm(initial={"theme": self.get_theme(), "scale": self.get_scale()})
        context["current_page_contribution_list"] = True
        return context
