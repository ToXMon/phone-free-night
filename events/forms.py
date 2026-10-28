from django import forms

from .models import Event, GuestSession, Lead


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "venue_name",
            "starts_at",
            "ends_at",
            "sponsor_name",
            "sponsor_prize",
        ]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class GuestJoinForm(forms.ModelForm):
    join_code = forms.CharField(max_length=6, label="Join code")

    class Meta:
        model = GuestSession
        fields = ["display_name", "team_name"]

    def clean_join_code(self):
        return self.cleaned_data["join_code"].strip().upper()


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["email", "name", "venue_name"]
