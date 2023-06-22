from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, FormView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from taggit.models import Tag

from event.forms import ContributionListFilterForm, EventListFilterForm, EventRegistrationForm
from event.models import Booking, Contribution, Event
from utils.emails import send_email


class EventListView(ListView):
    model = Event
    paginate_by = 10

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

        context["contributions"] = Contribution.objects.filter(event=self.object, public=True).prefetch_related("tags")
        context["current_page_event_list"] = True
        return context


class EventRegistrationView(LoginRequiredMixin, FormView):
    template_name = "event/event_registration.html"
    form_class = EventRegistrationForm

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs.get("pk"))

    def form_valid(self, form):
        form.instance.event = self.get_event()
        form.instance.participant = self.request.user
        send_email(
            to=[
                {
                    "name": f"{form.instance.participant.first_name} {form.instance.participant.last_name}",
                    "email": form.instance.participant.email,
                }
            ],
            params={"event_subject": form.instance.event.subject},
            template_id=settings.BREVO_PARTICIPATION_RECEIVED_TEMPLATE,
        )
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
    paginate_by = 10

    def get_theme(self):
        filter_theme = self.request.GET.get("theme", None)
        return filter_theme if filter_theme in Event.Theme.values else None

    def get_tag(self):
        filter_tag = self.request.GET.get("tag", None)
        return filter_tag if (filter_tag,) in Tag.objects.values_list("slug") else None

    def get_scale(self):
        filter_scale = self.request.GET.get("scale", None)
        return filter_scale if filter_scale in Event.Scale.values else None

    def get_queryset(self):
        qs = Contribution.objects.filter(event__pub_status=Event.PubStatus.PUB, public=True)

        filter_theme = self.get_theme()
        if filter_theme:
            qs = qs.filter(event__theme=filter_theme)

        filter_tag = self.get_tag()
        if filter_tag:
            qs = qs.filter(tags__slug=filter_tag)

        filter_scale = self.get_scale()
        if filter_scale:
            qs = qs.filter(event__scale=filter_scale)
        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = ContributionListFilterForm(
            initial={"theme": self.get_theme(), "tag": self.get_tag(), "scale": self.get_scale()}
        )
        context["current_page_contribution_list"] = True
        return context


class ContributionDetailView(UserPassesTestMixin, DetailView):
    model = Contribution

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user == self.get_object().event.owner:
            return True

        return self.get_object().public
