from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowDetailSerializer,
    AstronomyShowListSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    PlanetariumDomeSerializer,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly


class ShowThemeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    authentication_classes = (
        JWTAuthentication,
    )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlanetariumDomeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    authentication_classes = (
        JWTAuthentication,
    )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer
    authentication_classes = (
        JWTAuthentication,
    )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the astronomy shows with filters"""
        title = self.request.query_params.get("title")
        show_theme = self.request.query_params.get("show_theme")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if show_theme:
            show_theme_ids = self._params_to_ints(show_theme)
            queryset = queryset.filter(show_theme__id__in=show_theme_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer

        if self.action == "retrieve":
            return AstronomyShowDetailSerializer

        return AstronomyShowSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type={"type": "string"},
                description="Filter by title id (ex. ?titles=Looper)",
            ),
            OpenApiParameter(
                name="show theme",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by show theme id (ex. ?show theme=1,4)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of astronomy shows."""
        return super().list(request, *args, **kwargs)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = (
        ShowSession.objects.all()
        .select_related("astronomy_show", "planetarium_dome")
        .annotate(
            tickets_available=(
                F("planetarium_dome__rows")
                * F("planetarium_dome__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = ShowSessionSerializer
    authentication_classes = (
        JWTAuthentication,
    )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date")
        astronomy_show_id_str = self.request.query_params.get("astronomy_show")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if astronomy_show_id_str:
            queryset = queryset.filter(
                astronomy_show_id=int(astronomy_show_id_str)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer

        if self.action == "retrieve":
            return ShowSessionDetailSerializer

        return ShowSessionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type={"type": "string", "format": "date"},
                description="Filter by date id (ex. ?date=2024-10-10)",
            ),
            OpenApiParameter(
                name="astronomy show",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by astronomy show id"
                            " (ex. ?astronomy show=4)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of astronomy show sessions."""
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome"
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    authentication_classes = (
        JWTAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
