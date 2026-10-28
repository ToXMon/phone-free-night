from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EventForm, GuestJoinForm, LeadForm
from .models import Event, GuestSession


def home(request):
    events = Event.objects.filter(status__in=[Event.STATUS_LIVE, Event.STATUS_PAUSED])[
        :20
    ]
    return render(request, "events/home.html", {"events": events})


@login_required
def event_list(request):
    events = request.user.events.all()
    return render(request, "events/event_list.html", {"events": events})


@login_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            return redirect("event-detail", pk=event.pk)
    else:
        form = EventForm()
    return render(request, "events/event_form.html", {"form": form})


def _host_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.host != request.user:
        raise Http404
    return event


@login_required
def event_detail(request, pk):
    event = _host_event(request, pk)
    return render(
        request,
        "events/event_detail.html",
        {"event": event, "guests": event.leaderboard()},
    )


@login_required
@require_POST
def event_set_status(request, pk, status):
    event = _host_event(request, pk)
    if status in dict(Event.STATUS_CHOICES):
        event.status = status
        event.save()
    return redirect("event-detail", pk=event.pk)


@login_required
@require_POST
def event_raffle(request, pk):
    event = _host_event(request, pk)
    event.draw_raffle()
    return redirect("event-detail", pk=event.pk)


def guest_join(request):
    if request.method == "POST":
        form = GuestJoinForm(request.POST)
        if form.is_valid():
            event = Event.objects.filter(
                join_code=form.cleaned_data["join_code"]
            ).first()
            if not event:
                form.add_error("join_code", "No event found for that code.")
            else:
                guest = form.save(commit=False)
                guest.event = event
                guest.save()
                return redirect("guest-live", token=guest.token)
    else:
        form = GuestJoinForm()
    return render(request, "events/guest_join.html", {"form": form})


def guest_live(request, token):
    guest = get_object_or_404(GuestSession, token=token)
    return render(
        request,
        "events/guest_live.html",
        {"guest": guest, "event": guest.event},
    )


@require_POST
def guest_toggle(request, token):
    guest = get_object_or_404(GuestSession, token=token)
    guest.toggle_lock()
    return redirect("guest-live", token=guest.token)


def leaderboard_fragment(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(
        request,
        "events/_leaderboard.html",
        {"event": event, "guests": event.leaderboard()},
    )


def starter_kit(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("starter-kit-download")
    else:
        form = LeadForm()
    return render(request, "landing/starter_kit.html", {"form": form})


def starter_kit_download(request):
    return render(request, "landing/starter_kit_download.html")


def starter_kit_table_tent(request):
    return render(request, "landing/table_tent.html")


def starter_kit_host_script(request):
    return render(request, "landing/host_script.html")
