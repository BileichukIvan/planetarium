from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)


class PlanetariumModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )
        self.show_theme = ShowTheme.objects.create(name="Solar System")
        self.dome = PlanetariumDome.objects.create(name="Main Dome", rows=10, seats_in_row=20)
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
        self.reservation = Reservation.objects.create(user=self.user)

    def test_show_theme_str(self):
        self.assertEqual(str(self.show_theme), "Solar System")

    def test_astronomy_show_str(self):
        self.assertEqual(str(self.astronomy_show), "Exploring the Solar System")

    def test_planetarium_dome_str(self):
        self.assertEqual(str(self.dome), "Main Dome")

    def test_show_session_str(self):
        self.assertEqual(
            str(self.show_session),
            "Exploring the Solar System at 2024-08-20 19:00:00+00:00 in Main Dome"
        )

    def test_reservation_str(self):
        self.assertEqual(
            str(self.reservation),
            f"Reservation by {self.user.username} on {self.reservation.created_at}"
        )

    def test_ticket_str(self):
        ticket = Ticket.objects.create(
            row=5, seat=10, show_session=self.show_session, reservation=self.reservation
        )
        self.assertEqual(
            str(ticket),
            f"Ticket for {self.show_session} in row {ticket.row}, seat {ticket.seat}"
        )

    def test_ticket_validation(self):
        with self.assertRaises(ValidationError):
            ticket = Ticket(
                row=15, seat=25, show_session=self.show_session, reservation=self.reservation
            )
            ticket.full_clean()

    def test_planetarium_dome_capacity(self):
        self.assertEqual(self.dome.capacity, 200)
