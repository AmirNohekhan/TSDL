"""Small, dependency-free 3D vector and matrix operations."""

from __future__ import annotations

import math
from typing import TypeAlias

Vector3: TypeAlias = tuple[float, float, float]
Matrix3: TypeAlias = tuple[Vector3, Vector3, Vector3]


def add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def subtract(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scale(value: Vector3, factor: float) -> Vector3:
    return (value[0] * factor, value[1] * factor, value[2] * factor)


def dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(value: Vector3) -> float:
    return math.sqrt(dot(value, value))


def normalize(value: Vector3) -> Vector3:
    magnitude = norm(value)
    if magnitude <= 1e-15:
        raise ValueError("Cannot normalize a zero-length vector")
    return scale(value, 1.0 / magnitude)


def identity() -> Matrix3:
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def outer(value: Vector3) -> Matrix3:
    return tuple(tuple(value[i] * value[j] for j in range(3)) for i in range(3))  # type: ignore[return-value]


def matrix_add(a: Matrix3, b: Matrix3) -> Matrix3:
    return tuple(tuple(a[i][j] + b[i][j] for j in range(3)) for i in range(3))  # type: ignore[return-value]


def matrix_scale(matrix: Matrix3, factor: float) -> Matrix3:
    return tuple(tuple(cell * factor for cell in row) for row in matrix)  # type: ignore[return-value]


def matrix_vector(matrix: Matrix3, value: Vector3) -> Vector3:
    return tuple(dot(row, value) for row in matrix)  # type: ignore[return-value]


def solve_3x3(matrix: Matrix3, rhs: Vector3) -> Vector3:
    """Solve a 3x3 system with partial-pivot Gaussian elimination."""
    augmented = [list(matrix[row]) + [rhs[row]] for row in range(3)]
    for column in range(3):
        pivot = max(range(column, 3), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("Triangulation geometry is singular or nearly parallel")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(3):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                augmented[row][item] - factor * augmented[column][item] for item in range(4)
            ]
    return (augmented[0][3], augmented[1][3], augmented[2][3])

