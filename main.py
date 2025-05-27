from __future__ import annotations

import signal
import sys
import shutil
import time
from dataclasses import dataclass, field
from typing import Final

import numpy as np
from numpy.typing import NDArray


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
            self.canvas_size * self.viewer_distance * 3 / (8 * (self.inner_radius + self.outer_radius)),
        )

    def render_frame(self, angle_theta: float, angle_phi: float) -> NDArray[str]:
        cos_theta = np.cos(angle_theta)
        sin_theta = np.sin(angle_theta)
        cos_phi = np.cos(angle_phi)
        sin_phi = np.sin(angle_phi)

        pixel_buffer: NDArray[str] = np.full((self.canvas_size, self.canvas_size), " ")
        depth_buffer: NDArray[float] = np.zeros((self.canvas_size, self.canvas_size))

        phi_values = np.arange(0, 2 * np.pi, self.delta_phi)
        theta_values = np.arange(0, 2 * np.pi, self.delta_theta)
        cos_phi_vals = np.cos(phi_values)
        sin_phi_vals = np.sin(phi_values)
        cos_theta_vals = np.cos(theta_values)
        sin_theta_vals = np.sin(theta_values)
        circle_x_values = self.outer_radius + self.inner_radius * cos_theta_vals
        circle_y_values = self.inner_radius * sin_theta_vals

        x = (
            np.outer(cos_phi * cos_phi_vals + sin_theta * sin_phi * sin_phi_vals, circle_x_values)
            - circle_y_values * cos_theta * sin_phi
        ).T
        y = (
            np.outer(sin_phi * cos_phi_vals - sin_theta * cos_phi * sin_phi_vals, circle_x_values)
            + circle_y_values * cos_theta * cos_phi
        ).T
        z = (self.viewer_distance + cos_theta * np.outer(sin_phi_vals, circle_x_values) + circle_y_values * sin_theta).T
        ooz = 1 / z
        xp = (self.canvas_size / 2 + self.projection_constant * ooz * x).astype(int)
        yp = (self.canvas_size / 2 - self.projection_constant * ooz * y).astype(int)

        luminance_layer1 = (
            np.outer(cos_phi_vals, cos_theta_vals) * sin_phi - cos_theta * np.outer(sin_phi_vals, cos_theta_vals)
        ) - sin_theta * sin_theta_vals
        luminance_layer2 = cos_phi * (cos_theta * sin_theta_vals - np.outer(sin_phi_vals, cos_theta_vals * sin_theta))
        luminance_index = np.around((luminance_layer1 + luminance_layer2) * 8).astype(int).T

        valid_luminance_mask = luminance_index >= 0
        luminance_frame_chars = self.luminance_chars[luminance_index]

        for i in range(self.canvas_size):
            mask = valid_luminance_mask[i] & (ooz[i] > depth_buffer[xp[i], yp[i]])
            depth_buffer[xp[i], yp[i]] = np.where(mask, ooz[i], depth_buffer[xp[i], yp[i]])
            pixel_buffer[xp[i], yp[i]] = np.where(mask, luminance_frame_chars[i], pixel_buffer[xp[i], yp[i]])

        return pixel_buffer


def main() -> None:
    terminal_cols, terminal_rows = shutil.get_terminal_size()
    canvas_size = min(terminal_rows, terminal_cols // 2)
    renderer = DonutRenderer(canvas_size)
    angle_theta = 1.0
    angle_phi = 1.0

    # noinspection PyUnusedLocal
    def handle_exit(_signum: int, _frame: None | object) -> None:
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # Hide cursor for better visuals
    print("\x1b[?25l", end="")
    try:
        while True:
            angle_theta += renderer.delta_theta
            angle_phi += renderer.delta_phi
            print("\x1b[H", end="")
            frame = renderer.render_frame(angle_theta, angle_phi)
            time.sleep(0.05)
            for row in frame:
                print(" ".join(row))
    finally:
        # Show the cursor again on exit
        print("\x1b[?25h", end="")


if __name__ == "__main__":
    main()
