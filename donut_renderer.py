from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Final
from numpy.typing import NDArray

from donut_math import compute_frame


@dataclass(frozen=True)
class DonutRenderer:
    canvas_size: int
    delta_theta: Final[float] = 0.07
    delta_phi: Final[float] = 0.02
    inner_radius: Final[float] = 1.0
    outer_radius: Final[float] = 2.0
    viewer_distance: Final[float] = 5.0
    projection_constant: float = field(init=False)
    luminance_chars: NDArray[str] = field(
        default_factory=lambda: np.array(list(".,-~:;=!*#$@"))
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "projection_constant",
            self.canvas_size
            * self.viewer_distance
            * 3
            / (8 * (self.inner_radius + self.outer_radius)),
        )

    def render_frame(self, angle_theta: float, angle_phi: float) -> NDArray[str]:
        return compute_frame(
            angle_theta,
            angle_phi,
            self.canvas_size,
            self.inner_radius,
            self.outer_radius,
            self.viewer_distance,
            self.projection_constant,
            self.delta_theta,
            self.delta_phi,
            self.luminance_chars,
        )
