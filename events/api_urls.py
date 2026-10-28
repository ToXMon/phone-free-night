from django.urls import path
from rest_framework.generics import RetrieveAPIView

from .models import Event
from .serializers import EventSerializer


class EventLeaderboardAPIView(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


urlpatterns = [
    path(
        "events/<int:pk>/leaderboard/",
        EventLeaderboardAPIView.as_view(),
        name="api-event-leaderboard",
    ),
]
