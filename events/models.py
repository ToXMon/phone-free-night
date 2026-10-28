import hashlib
import random
import secrets
import string
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def make_join_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))


class Event(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_LIVE = "live"
    STATUS_PAUSED = "paused"
    STATUS_ENDED = "ended"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_LIVE, "Live"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ENDED, "Ended"),
    ]

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=200, default="Trivia Night")
    venue_name = models.CharField(max_length=200, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    join_code = models.CharField(max_length=6, unique=True, default=make_join_code)
    sponsor_name = models.CharField(max_length=200, blank=True)
    sponsor_prize = models.CharField(max_length=300, blank=True)
    raffle_seed_hash = models.CharField(max_length=64, blank=True)
    raffle_seed = models.CharField(max_length=100, blank=True)
    raffle_winner = models.ForeignKey(
        "GuestSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raffle_wins",
    )
    raffle_drawn_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]

    def __str__(self):
        return f"{self.title} ({self.join_code})"

    def leaderboard(self):
        return self.guests.order_by("-phone_free_minutes", "joined_at")

    def draw_raffle(self):
        """Draw once, weighted by raffle entries. Idempotent on re-call."""
        if self.raffle_winner:
            return self.raffle_winner
        guests = list(self.guests.all())
        if not guests:
            return None
        if not self.raffle_seed:
            seed = secrets.token_hex(16)
            self.raffle_seed = seed
            self.raffle_seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        rng = random.Random(self.raffle_seed)
        pool = []
        for guest in guests:
            pool.extend([guest] * max(guest.raffle_entries, 1))
        winner = rng.choice(pool)
        self.raffle_winner = winner
        self.raffle_drawn_at = timezone.now()
        self.save()
        return winner


class GuestSession(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="guests")
    display_name = models.CharField(max_length=100)
    team_name = models.CharField(max_length=100, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone_free_minutes = models.IntegerField(default=0)
    unlock_count = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=True)
    lock_started_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-phone_free_minutes", "joined_at"]

    def __str__(self):
        return f"{self.display_name} at {self.event.join_code}"

    @property
    def raffle_entries(self):
        # One entry per 10 phone-free minutes, plus one for joining.
        return 1 + self.phone_free_minutes // 10

    def current_locked_minutes(self):
        if not self.is_locked or not self.lock_started_at:
            return 0
        delta = timezone.now() - self.lock_started_at
        return int(delta.total_seconds() // 60)

    def toggle_lock(self):
        """Accrue minutes only while the event is live, then flip state."""
        now = timezone.now()
        if self.is_locked and self.event.status == Event.STATUS_LIVE:
            if self.lock_started_at:
                delta = now - self.lock_started_at
                self.phone_free_minutes += int(delta.total_seconds() // 60)
            self.unlock_count += 1
            self.is_locked = False
            self.lock_started_at = None
        elif not self.is_locked:
            self.is_locked = True
            self.lock_started_at = now
        self.save()
        return self


class Lead(models.Model):
    """A host who asked for the free Starter Kit. Email capture only."""

    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True)
    venue_name = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=100, default="starter-kit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
