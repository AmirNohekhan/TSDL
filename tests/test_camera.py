import math

import pytest

from tsdl.geometry.camera import CameraIntrinsics, pixel_to_camera_ray


def test_principal_point_maps_to_optical_axis() -> None:
    intrinsics = CameraIntrinsics(1000, 1000, 640, 360, 1280, 720)
    assert pixel_to_camera_ray(640, 360, intrinsics) == (0.0, 0.0, 1.0)


def test_off_axis_ray_is_normalized() -> None:
    intrinsics = CameraIntrinsics(1000, 900, 640, 360, 1280, 720)
    ray = pixel_to_camera_ray(740, 270, intrinsics)
    assert math.sqrt(sum(component**2 for component in ray)) == pytest.approx(1.0)
    assert ray[0] > 0
    assert ray[1] < 0


def test_rejects_uncalibrated_pixel_bounds() -> None:
    intrinsics = CameraIntrinsics(1000, 1000, 640, 360, 1280, 720)
    with pytest.raises(ValueError, match="outside"):
        pixel_to_camera_ray(1280, 200, intrinsics)

