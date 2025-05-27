from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.reactive import reactive

from donut_renderer import DonutRenderer


class DonutWidget(Static):
    angle_theta: float = reactive(1.0)
    angle_phi: float = reactive(1.0)
    renderer: DonutRenderer

    def on_mount(self) -> None:
        widget_size = self.app.size
        canvas_size = min(widget_size.height, widget_size.width)
        self.renderer = DonutRenderer(canvas_size=canvas_size)
        # Disable wrapping to preserve whitespace
        self.styles.no_wrap = True
        self.set_interval(0.05, self.refresh_frame)
        self.refresh_frame()

    def refresh_frame(self) -> None:
        frame = self.renderer.render_frame(
            angle_theta=self.angle_theta,
            angle_phi=self.angle_phi,
        )
        self.angle_theta += self.renderer.delta_theta
        self.angle_phi += self.renderer.delta_phi
        text = "\n".join("".join(char * 2 for char in row) for row in frame)
        self.update(text)


class DonutApp(App):
    def compose(self) -> ComposeResult:
        yield DonutWidget()


if __name__ == "__main__":
    DonutApp().run()
