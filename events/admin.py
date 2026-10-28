from django.contrib import admin

from .models import Event, GuestSession, Lead


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "venue_name", "host", "status", "join_code", "starts_at"]
    list_filter = ["status"]
    search_fields = ["title", "venue_name", "join_code"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(host=request.user)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "venue_name", "source", "created_at"]
    search_fields = ["email", "venue_name"]


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "team_name",
        "event",
        "phone_free_minutes",
        "unlock_count",
    ]
    list_filter = ["event"]
    search_fields = ["display_name", "team_name"]
