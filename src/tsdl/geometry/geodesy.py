"""WGS84/ECEF transformations using latitude, longitude, altitude ordering."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .vector import Vector3

WGS84_A_M = 6_378_137.0
WGS84_F = 1.0 / 298.257_223_563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)


@dataclass(frozen=True)
class GeodeticPoint:
    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError("Latitude must be in [-90, 90]")
        if not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError("Longitude must be in [-180, 180]")


def wgs84_to_ecef(point: GeodeticPoint) -> Vector3:
    latitude = math.radians(point.latitude_deg)
    longitude = math.radians(point.longitude_deg)
    sin_latitude = math.sin(latitude)
    prime_vertical = WGS84_A_M / math.sqrt(1.0 - WGS84_E2 * sin_latitude**2)
    radial = (prime_vertical + point.altitude_m) * math.cos(latitude)
    return (
        radial * math.cos(longitude),
        radial * math.sin(longitude),
        (prime_vertical * (1.0 - WGS84_E2) + point.altitude_m) * sin_latitude,
    )


def ecef_to_wgs84(ecef: Vector3) -> GeodeticPoint:
    """Iteratively convert ECEF to WGS84, including poles and altitude."""
    x, y, z = ecef
    longitude = math.atan2(y, x)
    horizontal = math.hypot(x, y)
    if horizontal < 1e-9:
        latitude = math.copysign(math.pi / 2.0, z)
        polar_radius = WGS84_A_M * math.sqrt(1.0 - WGS84_E2)
        return GeodeticPoint(math.degrees(latitude), 0.0, abs(z) - polar_radius)
    latitude = math.atan2(z, horizontal * (1.0 - WGS84_E2))
    altitude = 0.0
    for _ in range(15):
        sin_latitude = math.sin(latitude)
        prime_vertical = WGS84_A_M / math.sqrt(1.0 - WGS84_E2 * sin_latitude**2)
        altitude = horizontal / math.cos(latitude) - prime_vertical
        updated = math.atan2(
            z,
            horizontal * (1.0 - WGS84_E2 * prime_vertical / (prime_vertical + altitude)),
        )
        if abs(updated - latitude) < 1e-13:
            latitude = updated
            break
        latitude = updated
    return GeodeticPoint(math.degrees(latitude), math.degrees(longitude), altitude)

