import numpy as np
from numpy.typing import NDArray
from typing import Final


def compute_frame(
    angle_theta: float,
    angle_phi: float,
    canvas_size: int,
    inner_radius: float,
    outer_radius: float,
    viewer_distance: float,
    projection_constant: float,
    delta_theta: float,
    delta_phi: float,
    luminance_chars: NDArray[str],
) -> NDArray[str]:
    cos_theta = np.cos(angle_theta)
    sin_theta = np.sin(angle_theta)
    cos_phi = np.cos(angle_phi)
    sin_phi = np.sin(angle_phi)

    pixel_buffer: NDArray[str] = np.full((canvas_size, canvas_size), " ")
    depth_buffer: NDArray[float] = np.zeros((canvas_size, canvas_size))

    phi_values = np.arange(0, 2 * np.pi, delta_phi)
    theta_values = np.arange(0, 2 * np.pi, delta_theta)
    cos_phi_vals = np.cos(phi_values)
    sin_phi_vals = np.sin(phi_values)
    cos_theta_vals = np.cos(theta_values)
    sin_theta_vals = np.sin(theta_values)
    circle_x_values = outer_radius + inner_radius * cos_theta_vals
    circle_y_values = inner_radius * sin_theta_vals

    x = (
        np.outer(
            cos_phi * cos_phi_vals + sin_theta * sin_phi * sin_phi_vals, circle_x_values
        )
        - circle_y_values * cos_theta * sin_phi
    ).T
    y = (
        np.outer(
            sin_phi * cos_phi_vals - sin_theta * cos_phi * sin_phi_vals, circle_x_values
        )
        + circle_y_values * cos_theta * cos_phi
    ).T
    z = (
        viewer_distance
        + cos_theta * np.outer(sin_phi_vals, circle_x_values)
        + circle_y_values * sin_theta
    ).T
    ooz = 1 / z

    xp = (canvas_size / 2 + projection_constant * ooz * x).astype(int)
    yp = (canvas_size / 2 - projection_constant * ooz * y).astype(int)
    xp = np.clip(xp, 0, canvas_size - 1)
    yp = np.clip(yp, 0, canvas_size - 1)

    luminance_layer1 = (
        np.outer(cos_phi_vals, cos_theta_vals) * sin_phi
        - cos_theta * np.outer(sin_phi_vals, cos_theta_vals)
    ) - sin_theta * sin_theta_vals
    luminance_layer2 = cos_phi * (
        cos_theta * sin_theta_vals - np.outer(sin_phi_vals, cos_theta_vals * sin_theta)
    )
    luminance_index = np.around((luminance_layer1 + luminance_layer2) * 8).astype(int).T
    # Brighten shading by biasing luminance
    brightness_bias: Final[int] = 2
    max_index: int = luminance_chars.shape[0] - 1
    luminance_index = np.clip(luminance_index + brightness_bias, 0, max_index)

    valid_luminance_mask = luminance_index >= 0
    luminance_frame_chars = luminance_chars[luminance_index]

    for i in range(canvas_size):
        mask = valid_luminance_mask[i] & (ooz[i] > depth_buffer[xp[i], yp[i]])
        depth_buffer[xp[i], yp[i]] = np.where(mask, ooz[i], depth_buffer[xp[i], yp[i]])
        pixel_buffer[xp[i], yp[i]] = np.where(
            mask, luminance_frame_chars[i], pixel_buffer[xp[i], yp[i]]
        )

    return pixel_buffer
