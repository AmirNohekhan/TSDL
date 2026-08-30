"""Pinhole-camera primitives with explicit pixel conventions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .vector import Vector3, normalize


class PixelReference(StrEnum):
    """Physical feature represented by an image coordinate."""

    BOUNDING_BOX_CENTER = "BOUNDING_BOX_CENTER"
    BOUNDING_BOX_BOTTOM_CENTER = "BOUNDING_BOX_BOTTOM_CENTER"


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.fx <= 0 or self.fy <= 0:
            raise ValueError("Focal lengths must be positive")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive")


def pixel_to_camera_ray(u: float, v: float, intrinsics: CameraIntrinsics) -> Vector3:
    """Return a unit ray in the OpenCV optical frame: +x right, +y down, +z forward."""
    if not (0.0 <= u < intrinsics.width and 0.0 <= v < intrinsics.height):
        raise ValueError("Pixel is outside the calibrated image bounds")
    return normalize(
        (
            (u - intrinsics.cx) / intrinsics.fx,
            (v - intrinsics.cy) / intrinsics.fy,
            1.0,
        )
    )

