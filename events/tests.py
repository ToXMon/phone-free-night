from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Event, GuestSession


class PhoneFreeNightTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.host = user_model.objects.create_user(
            username="host", password="testpass123"
        )
        self.event = Event.objects.create(
            host=self.host,
            title="Trivia Night",
            venue_name="Test Bar",
            starts_at=timezone.now(),
            status=Event.STATUS_LIVE,
        )

    def test_guest_join_creates_session(self):
        guest = GuestSession.objects.create(
            event=self.event, display_name="Sam", team_name="Winners"
        )
        self.assertEqual(guest.raffle_entries, 1)
        self.assertTrue(guest.is_locked)

    def test_lock_toggle_accrues_minutes_only_when_live(self):
        guest = GuestSession.objects.create(
            event=self.event,
            display_name="Sam",
            is_locked=True,
            lock_started_at=timezone.now() - timedelta(minutes=30),
        )
        guest.toggle_lock()
        self.assertEqual(guest.phone_free_minutes, 30)
        self.assertEqual(guest.unlock_count, 1)
        self.assertFalse(guest.is_locked)

    def test_leaderboard_orders_by_minutes(self):
        low = GuestSession.objects.create(
            event=self.event, display_name="Low", phone_free_minutes=5
        )
        high = GuestSession.objects.create(
            event=self.event, display_name="High", phone_free_minutes=40
        )
        self.assertEqual(list(self.event.leaderboard()), [high, low])

    def test_starter_kit_landing_and_lead_capture(self):
        response = self.client.get("/starter-kit/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/starter-kit/",
            {"email": "host@example.com", "name": "Sam", "venue_name": "Test Bar"},
        )
        self.assertEqual(response.status_code, 302)
        from .models import Lead

        self.assertTrue(Lead.objects.filter(email="host@example.com").exists())
        response = self.client.get("/starter-kit/download/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/starter-kit/table-tent/")
        self.assertEqual(response.status_code, 200)

    def test_raffle_draw_is_idempotent(self):
        guest = GuestSession.objects.create(event=self.event, display_name="Sam")
        first = self.event.draw_raffle()
        second = self.event.draw_raffle()
        self.assertEqual(first, guest)
        self.assertEqual(second, guest)
        self.assertTrue(self.event.raffle_seed_hash)
