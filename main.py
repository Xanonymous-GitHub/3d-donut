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
    screen_size: int
    theta_spacing: Final[float] = 0.07
    phi_spacing: Final[float] = 0.02
    R1: Final[float] = 1.0
    R2: Final[float] = 2.0
    K2: Final[float] = 5.0
    K1: float = field(init=False)
    illumination: NDArray[str] = field(
        default_factory=lambda: np.array(list(".,-~:;=!*#$@"))
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "K1",
            self.screen_size * self.K2 * 3 / (8 * (self.R1 + self.R2)),
        )

    def render_frame(self, a: float, b: float) -> NDArray[str]:
        cos_a = np.cos(a)
        sin_a = np.sin(a)
        cos_b = np.cos(b)
        sin_b = np.sin(b)

        output: NDArray[str] = np.full((self.screen_size, self.screen_size), " ")
        z_buffer: NDArray[float] = np.zeros((self.screen_size, self.screen_size))

        phi = np.arange(0, 2 * np.pi, self.phi_spacing)
        theta = np.arange(0, 2 * np.pi, self.theta_spacing)
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        circle_x = self.R2 + self.R1 * cos_theta
        circle_y = self.R1 * sin_theta

        x = (
            np.outer(cos_b * cos_phi + sin_a * sin_b * sin_phi, circle_x)
            - circle_y * cos_a * sin_b
        ).T
        y = (
            np.outer(sin_b * cos_phi - sin_a * cos_b * sin_phi, circle_x)
            + circle_y * cos_a * cos_b
        ).T
        z = (self.K2 + cos_a * np.outer(sin_phi, circle_x) + circle_y * sin_a).T
        ooz = 1 / z
        xp = (self.screen_size / 2 + self.K1 * ooz * x).astype(int)
        yp = (self.screen_size / 2 - self.K1 * ooz * y).astype(int)

        l1 = (
            np.outer(cos_phi, cos_theta) * sin_b - cos_a * np.outer(sin_phi, cos_theta)
        ) - sin_a * sin_theta
        l2 = cos_b * (cos_a * sin_theta - np.outer(sin_phi, cos_theta * sin_a))
        l = np.around((l1 + l2) * 8).astype(int).T

        mask_l = l >= 0
        chars = self.illumination[l]

        for i in range(self.screen_size):
            mask = mask_l[i] & (ooz[i] > z_buffer[xp[i], yp[i]])
            z_buffer[xp[i], yp[i]] = np.where(mask, ooz[i], z_buffer[xp[i], yp[i]])
            output[xp[i], yp[i]] = np.where(mask, chars[i], output[xp[i], yp[i]])

        return output


def main() -> None:
    columns, lines = shutil.get_terminal_size()
    screen_size = min(lines, columns // 2)
    renderer = DonutRenderer(screen_size)
    a = 1.0
    b = 1.0

    # noinspection PyUnusedLocal
    def handle_exit(_signum: int, _frame: None | object) -> None:
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # Hide cursor for better visuals
    print("\x1b[?25l", end="")
    try:
        while True:
            a += renderer.theta_spacing
            b += renderer.phi_spacing
            print("\x1b[H", end="")
            frame = renderer.render_frame(a, b)
            time.sleep(0.05)
            for row in frame:
                print(" ".join(row))
    finally:
        # Show the cursor again on exit
        print("\x1b[?25h", end="")


if __name__ == "__main__":
    main()
