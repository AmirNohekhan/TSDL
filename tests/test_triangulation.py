import math

import pytest

from tsdl.geometry.triangulation import RayObservation, triangulate_rays


def direction(origin: tuple[float, float, float], target: tuple[float, float, float]):
    delta = tuple(target[index] - origin[index] for index in range(3))
    magnitude = math.sqrt(sum(component**2 for component in delta))
    return tuple(component / magnitude for component in delta)


def test_reconstructs_known_sign_from_multiple_views() -> None:
    sign = (12.0, 25.0, 2.5)
    origins = [(0.0, 0.0, 1.5), (8.0, 0.0, 1.5), (16.0, 0.0, 1.5)]
    observations = [RayObservation(origin, direction(origin, sign)) for origin in origins]
    result = triangulate_rays(observations)
    assert result.position == pytest.approx(sign, abs=1e-9)
    assert result.rms_residual_m < 1e-9


def test_weights_reduce_influence_of_bad_ray() -> None:
    sign = (10.0, 20.0, 2.0)
    observations = [
        RayObservation((0.0, 0.0, 1.0), direction((0.0, 0.0, 1.0), sign), 10.0),
        RayObservation((10.0, 0.0, 1.0), direction((10.0, 0.0, 1.0), sign), 10.0),
        RayObservation((20.0, 0.0, 1.0), direction((20.0, 0.0, 1.0), (14.0, 20.0, 2.0)), 0.01),
    ]
    result = triangulate_rays(observations)
    assert result.position == pytest.approx(sign, abs=0.02)


def test_parallel_rays_are_rejected() -> None:
    with pytest.raises(ValueError, match="singular|parallel"):
        triangulate_rays(
            [
                RayObservation((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
                RayObservation((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
            ]
        )

