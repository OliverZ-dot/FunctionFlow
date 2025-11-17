"""Pretend rocket engine control logic."""


def ignite(fuel_level: float, oxidizer_level: float) -> bool:
    """Raise thrust if both tanks are healthy."""
    if fuel_level < 0.5 or oxidizer_level < 0.5:
        return False
    thrust = mix_propellants(fuel_level, oxidizer_level)
    telemetry(thrust)
    return thrust > 0


def mix_propellants(fuel: float, oxidizer: float) -> float:
    ratio = min(fuel, oxidizer)
    regulator(ratio)
    return ratio * 42


def regulator(flow: float) -> None:
    if flow > 1.5:
        bleed_valve(flow)


def bleed_valve(flow: float) -> None:
    pass


def telemetry(value: float) -> None:
    log_event("thrust", value)


def log_event(event: str, data: float) -> None:
    ...

