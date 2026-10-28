from rest_framework import serializers

from .models import Event, GuestSession


class GuestSessionSerializer(serializers.ModelSerializer):
    raffle_entries = serializers.ReadOnlyField()

    class Meta:
        model = GuestSession
        fields = [
            "display_name",
            "team_name",
            "phone_free_minutes",
            "unlock_count",
            "raffle_entries",
            "joined_at",
        ]


class EventSerializer(serializers.ModelSerializer):
    guests = GuestSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "venue_name",
            "status",
            "join_code",
            "sponsor_name",
            "sponsor_prize",
            "starts_at",
            "guests",
        ]
