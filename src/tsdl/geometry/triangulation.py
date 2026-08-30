"""Weighted least-squares intersection of world-space viewing rays."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .vector import (
    Matrix3,
    Vector3,
    add,
    identity,
    matrix_add,
    matrix_scale,
    matrix_vector,
    norm,
    normalize,
    outer,
    solve_3x3,
    subtract,
)


@dataclass(frozen=True)
class RayObservation:
    origin: Vector3
    direction: Vector3
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.weight <= 0 or not math.isfinite(self.weight):
            raise ValueError("Observation weight must be positive and finite")
        normalize(self.direction)


@dataclass(frozen=True)
class TriangulationResult:
    position: Vector3
    rms_residual_m: float
    max_residual_m: float
    observation_count: int


def triangulate_rays(observations: list[RayObservation]) -> TriangulationResult:
    """Find the point minimizing weighted squared perpendicular distance to rays.

    This is a line intersection estimate. Callers must separately enforce positive
    depth, baseline, accuracy, and uncertainty commit criteria.
    """
    if len(observations) < 2:
        raise ValueError("At least two observations are required")
    normal: Matrix3 = ((0.0, 0.0, 0.0),) * 3
    rhs: Vector3 = (0.0, 0.0, 0.0)
    projectors: list[tuple[Matrix3, RayObservation]] = []
    for observation in observations:
        direction = normalize(observation.direction)
        projector = matrix_add(identity(), matrix_scale(outer(direction), -1.0))
        weighted = matrix_scale(projector, observation.weight)
        normal = matrix_add(normal, weighted)
        rhs = add(rhs, matrix_vector(weighted, observation.origin))
        projectors.append((projector, observation))
    position = solve_3x3(normal, rhs)
    residuals = [
        norm(matrix_vector(projector, subtract(position, observation.origin)))
        for projector, observation in projectors
    ]
    weighted_square_sum = sum(
        observation.weight * residual**2
        for residual, (_, observation) in zip(residuals, projectors, strict=True)
    )
    weight_sum = sum(observation.weight for observation in observations)
    return TriangulationResult(
        position=position,
        rms_residual_m=math.sqrt(weighted_square_sum / weight_sum),
        max_residual_m=max(residuals),
        observation_count=len(observations),
    )
