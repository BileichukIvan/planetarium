from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)
from django.utils import timezone


class PlanetariumViewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )
        self.admin = get_user_model().objects.create_superuser(
            username="admin", password="adminpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

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
            show_time=timezone.now()
        )

    def test_create_show_theme(self):
        """Test creating a new show theme"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("planetarium:showtheme-list")
        data = {"name": "Galaxies"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShowTheme.objects.count(), 2)
        self.assertEqual(ShowTheme.objects.get(id=2).name, "Galaxies")

    def test_get_show_themes(self):
        """Test retrieving a list of show themes"""
        url = reverse("planetarium:showtheme-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_reservation(self):
        """Test creating a reservation"""
        url = reverse("planetarium:reservation-list")
        data = {
            "tickets": [
                {"row": 5, "seat": 10, "show_session": self.show_session.id},
                {"row": 6, "seat": 15, "show_session": self.show_session.id},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_get_reservations(self):
        """Test retrieving a list of reservations"""
        Reservation.objects.create(user=self.user)
        url = reverse("planetarium:reservation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_astronomy_shows(self):
        """Test listing astronomy shows with a filter"""
        url = reverse("planetarium:astronomyshow-list")
        response = self.client.get(url, {"title": "Solar"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"], "Exploring the Solar System"
        )

    def test_list_show_sessions(self):
        """Test listing show sessions"""
        url = reverse("planetarium:showsession-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_ticket_validation(self):
        """Test creating a ticket with validation errors"""
        url = reverse("planetarium:reservation-list")
        data = {
            "tickets": [
                {"row": 15, "seat": 25, "show_session": self.show_session.id},  # Invalid seat/row
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
