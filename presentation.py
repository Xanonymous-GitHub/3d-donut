from numpy.typing import NDArray


def hide_cursor() -> None:
    print("\x1b[?25l", end="")


def show_cursor() -> None:
    print("\x1b[?25h", end="")


def clear_and_reset_cursor() -> None:
    print("\x1b[H", end="")


def display_frame(frame: NDArray[str]) -> None:
    for row in frame:
        print(" ".join(row))
