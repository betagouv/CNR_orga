from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


class OrganizerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_organizer


class OrganizerDashboardView(OrganizerMixin, TemplateView):
    template_name = "event/organizer/dashboard.html"
