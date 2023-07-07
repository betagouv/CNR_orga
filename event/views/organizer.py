import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView, FormView, UpdateView, View
from django.views.generic.list import ListView

from event.forms import AddOrganizerForm, ContributionForm, EventForm
from event.models import Booking, Contribution, Event
from utils.emails import send_email


UserModel = get_user_model()


class OrganizerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_organizer


class OrganizerDashboardView(OrganizerMixin, ListView):
    model = Event
    fields = "__all__"
    template_name = "event/organizer/dashboard.html"

    def get_queryset(self):
        qs = Event.objects.filter(organizers__in=[self.request.user]).order_by("start")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["current_page_organizer_dashboard"] = True
        return context


class OrganizerEventCreateView(OrganizerMixin, FormView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        event = form.save()
        event.organizers.add(self.request.user)
        return super(OrganizerEventCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("event_organizer_dashboard")


class OrganizerEventDetailView(OrganizerMixin, DetailView):
    template_name = "event/organizer/event_detail.html"
    model = Event

    def get_object(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs["pk"], organizers__in=[self.request.user])
        return event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings"] = Booking.objects.filter(event=self.object)
        context["contributions"] = Contribution.objects.filter(event=self.object)
        return context


class OrganizerEventUpdateView(OrganizerMixin, UpdateView):
    template_name = "event/organizer/event_edit.html"
    form_class = EventForm

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Event, pk=self.kwargs["pk"], organizers__in=[self.request.user])

    def get_success_url(self):
        return reverse("event_organizer_event_detail", kwargs={"pk": self.object.pk})


class OrganizerEventParticipantsExportView(OrganizerMixin, View):
    def get_event(self, *args, **kwargs):
        return get_object_or_404(Event, pk=self.kwargs["pk"], organizers__in=[self.request.user])

    def get(self, request, *args, **kwargs):
        event = self.get_event()
        event_slug = slugify(event.subject)

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="participants-{event_slug}.csv"'},
        )
        writer = csv.writer(response, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", quotechar='"')
        writer.writerow(["Prénom", "Nom", "Email", "Aide", "Commentaire", "État"])

        bookings = Booking.objects.filter(event=event)
        for booking in bookings:
            if booking.confirmed_on:
                status = f"Confirmée le {booking.confirmed_on}"
            elif booking.cancelled_on:
                status = f"Déclinée le {booking.cancelled_on}"
            else:
                status = "En attente"

            writer.writerow(
                [
                    booking.participant.first_name,
                    booking.participant.last_name,
                    booking.participant.email,
                    "oui" if booking.offer_help else "non",
                    booking.comment.replace('"', "''"),
                    status,
                ]
            )

        return response


class OrganizerRegistrationBaseView(OrganizerMixin, View):
    def get_booking(self):
        if not hasattr(self, "booking"):
            self.booking = get_object_or_404(
                Booking,
                pk=self.kwargs["pk"],
                event__organizers__in=[self.request.user],  # only event organizer can view/edit booking
            )
        return self.booking


class OrganizerRegistrationAcceptView(OrganizerRegistrationBaseView):
    def post(self, request, **kwargs):
        booking = self.get_booking()
        booking.confirmed_on = timezone.now()
        send_email(
            to=[
                {
                    "name": f"{booking.participant.first_name} {booking.participant.last_name}",
                    "email": booking.participant.email,
                }
            ],
            params={"event_subject": booking.event.subject},
            template_id=settings.BREVO_PARTICIPATION_ACCEPTED_TEMPLATE,
        )
        booking.save()
        return render(request, "event/organizer/partials/booking_row.html", context={"booking": booking})


class OrganizerRegistrationDeclineView(OrganizerRegistrationBaseView):
    def post(self, request, **kwargs):
        booking = self.get_booking()
        booking.cancelled_on = timezone.now()
        booking.cancelled_by = request.user
        send_email(
            to=[
                {
                    "name": f"{booking.participant.first_name} {booking.participant.last_name}",
                    "email": booking.participant.email,
                }
            ],
            params={"event_subject": booking.event.subject},
            template_id=settings.BREVO_PARTICIPATION_DECLINE_TEMPLATE,
        )
        booking.save()
        return render(request, "event/organizer/partials/booking_row.html", context={"booking": booking})


class ContributionCreateView(OrganizerMixin, FormView):
    template_name = "event/organizer/contribution_edit.html"
    form_class = ContributionForm

    def get_initial(self):
        initial = super().get_initial()
        initial["public"] = True
        return initial

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs.get("event_pk"), organizers__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

    def form_valid(self, form):
        form.instance.event = self.get_event()
        form.save()
        return super(ContributionCreateView, self).form_valid(form)

    def get_success_url(self):
        if "submitandadd" in self.request.POST:
            return reverse("event_organizer_contribution_create", kwargs={"event_pk": self.kwargs.get("event_pk")})

        return reverse("event_organizer_event_detail", kwargs={"pk": self.kwargs.get("event_pk")})


class ContributionUpdateView(OrganizerMixin, UpdateView):
    template_name = "event/organizer/contribution_edit.html"
    form_class = ContributionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.object.event
        return context

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Contribution, pk=self.kwargs["pk"], event__organizers__in=[self.request.user])

    def get_initial(self):
        initial = super().get_initial()
        if self.object.current_status:
            initial["status"] = self.object.current_status.status
        return initial

    def get_success_url(self):
        return reverse("event_organizer_event_detail", kwargs={"pk": self.object.event.pk})


class OrganizerEventOrganizerAddView(OrganizerMixin, FormView):
    template_name = "event/organizer/event_add_organizer.html"
    form_class = AddOrganizerForm

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs.get("event_pk"), owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

    def form_valid(self, form):
        user = UserModel.objects.get(email=form.cleaned_data["email_organizer"])
        event = self.get_event()
        if user not in event.organizers.all():
            event.organizers.add(user)
            messages.success(self.request, f"{user} a été ajouté aux organisateurs avec succès.")
        else:
            messages.info(self.request, f"{user} fait déjà partie des organisateurs.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("event_organizer_event_detail", kwargs={"pk": self.kwargs.get("event_pk")})
