import pytest

from tsdl.geometry.geodesy import GeodeticPoint, ecef_to_wgs84, wgs84_to_ecef


@pytest.mark.parametrize(
    "point",
    [
        GeodeticPoint(0.0, 0.0, 0.0),
        GeodeticPoint(39.128473, -77.154821, 123.4),
        GeodeticPoint(-33.8688, 151.2093, 15.0),
        GeodeticPoint(89.9, 179.9, 1000.0),
    ],
)
def test_wgs84_ecef_round_trip(point: GeodeticPoint) -> None:
    recovered = ecef_to_wgs84(wgs84_to_ecef(point))
    assert recovered.latitude_deg == pytest.approx(point.latitude_deg, abs=1e-8)
    assert recovered.longitude_deg == pytest.approx(point.longitude_deg, abs=1e-8)
    assert recovered.altitude_m == pytest.approx(point.altitude_m, abs=1e-3)


def test_rejects_reversed_or_invalid_latitude() -> None:
    with pytest.raises(ValueError, match="Latitude"):
        GeodeticPoint(-120.0, 40.0)

