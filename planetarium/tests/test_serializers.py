from django.test import TestCase
from rest_framework.exceptions import ValidationError
from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    ShowSessionSerializer,
    TicketSerializer,
    ReservationSerializer,
)
from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
)


class PlanetariumSerializerTests(TestCase):

    def setUp(self):
        self.show_theme = ShowTheme.objects.create(name="Solar System")
        self.dome = PlanetariumDome.objects.create(
            name="Main Dome", rows=10, seats_in_row=20
        )
        self.astronomy_show = AstronomyShow.objects.create(
            title="Exploring the Solar System",
            description="A journey through the solar system."
        )
        self.astronomy_show.show_theme.add(self.show_theme)
        self.show_session = ShowSession.objects.create(
            astronomy_show=self.astronomy_show,
            planetarium_dome=self.dome,
            show_time="2024-08-20T19:00:00Z"
        )

    def test_show_theme_serializer(self):
        serializer = ShowThemeSerializer(instance=self.show_theme)
        self.assertEqual(serializer.data["name"], "Solar System")

    def test_astronomy_show_serializer(self):
        serializer = AstronomyShowSerializer(instance=self.astronomy_show)
        self.assertEqual(
            serializer.data["title"],
            "Exploring the Solar System"
        )
        self.assertEqual(
            serializer.data["description"],
            "A journey through the solar system."
        )

    def test_show_session_serializer(self):
        serializer = ShowSessionSerializer(instance=self.show_session)
        self.assertEqual(
            serializer.data["astronomy_show"],
            self.astronomy_show.id
        )

    def test_ticket_serializer_validation(self):
        data = {
            "row": 15,  # Invalid row
            "seat": 25,  # Invalid seat
            "show_session": self.show_session.id
        }
        serializer = TicketSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_reservation_serializer(self):
        reservation = Reservation.objects.create(user=self.user)
        data = {
            "tickets": [
                {"row": 5, "seat": 10, "show_session": self.show_session.id},
                {"row": 6, "seat": 15, "show_session": self.show_session.id},
            ]
        }
        serializer = ReservationSerializer(instance=reservation, data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["tickets"]), 2)
