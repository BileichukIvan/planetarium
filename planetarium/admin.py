from django.contrib import admin

from planetarium.models import (
    ShowSession,
    ShowTheme,
    AstronomyShow,
    Reservation,
    PlanetariumDome,
    Ticket,
)

admin.site.register(ShowTheme)
admin.site.register(ShowSession)
admin.site.register(AstronomyShow)
admin.site.register(Reservation)
admin.site.register(PlanetariumDome)
admin.site.register(Ticket)
