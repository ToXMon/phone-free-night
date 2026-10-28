from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("host/events/", views.event_list, name="event-list"),
    path("host/events/new/", views.event_create, name="event-create"),
    path("host/events/<int:pk>/", views.event_detail, name="event-detail"),
    path(
        "host/events/<int:pk>/status/<str:status>/",
        views.event_set_status,
        name="event-set-status",
    ),
    path("host/events/<int:pk>/raffle/", views.event_raffle, name="event-raffle"),
    path("join/", views.guest_join, name="guest-join"),
    path("guest/<uuid:token>/", views.guest_live, name="guest-live"),
    path("guest/<uuid:token>/toggle/", views.guest_toggle, name="guest-toggle"),
    path(
        "events/<int:pk>/leaderboard/",
        views.leaderboard_fragment,
        name="leaderboard-fragment",
    ),
    path("starter-kit/", views.starter_kit, name="starter-kit"),
    path(
        "starter-kit/download/",
        views.starter_kit_download,
        name="starter-kit-download",
    ),
    path(
        "starter-kit/table-tent/",
        views.starter_kit_table_tent,
        name="starter-kit-table-tent",
    ),
    path(
        "starter-kit/host-script/",
        views.starter_kit_host_script,
        name="starter-kit-host-script",
    ),
]
