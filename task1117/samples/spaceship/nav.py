"""Toy navigation stack."""

from math import hypot


def plot_course(origin: tuple[float, float], target: tuple[float, float]) -> float:
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]
    distance = hypot(dx, dy)
    return adjust_heading(distance)


def adjust_heading(distance: float) -> float:
    if distance > 100:
        engage_autopilot(distance)
    return distance / 10


def engage_autopilot(distance: float) -> None:
    log_mode("autopilot", distance)


def log_mode(mode: str, payload: float) -> None:
    ...

