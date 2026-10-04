#!/usr/bin/env python3
"""Robot status panel + sensor-visualisation toggle for
:class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings resolve on the concrete window via MRO.
"""


class StatusMixin:
    """Refreshing the Robot Status panel each frame, proximity warnings on
    the status bar, and the sensor-visualisation toggle."""

    def _update_status_panel(self):
        """Update the status panel with current robot state"""
        # Motors
        left, right = self.thymio.get_motor_speeds()
        self.left_motor_label.setText(f"L: {left}")
        self.right_motor_label.setText(f"R: {right}")

        # Proximity sensors
        for i, label in enumerate(self.prox_labels):
            value = self.thymio.sensors.proximity[i]
            names = ["FL", "L", "C", "R", "FR", "BL", "BR"]
            label.setText(f"Prox {names[i]}: {value}")

            # Color code based on value
            if value > 2000:
                label.setStyleSheet("color: red; font-size: 10px;")
            elif value > 500:
                label.setStyleSheet("color: orange; font-size: 10px;")
            else:
                label.setStyleSheet("color: green; font-size: 10px;")

        # Ground sensors
        gl = self.thymio.sensors.ground_delta[0]
        gr = self.thymio.sensors.ground_delta[1]
        self.ground_left_label.setText(f"Ground L: {gl}")
        self.ground_right_label.setText(f"Ground R: {gr}")

        # Color code ground sensors
        self.ground_left_label.setStyleSheet(
            "color: red;" if gl < 300 else "color: green;"
        )
        self.ground_right_label.setStyleSheet(
            "color: red;" if gr < 300 else "color: green;"
        )

        # Position
        self.pos_label.setText(f"X: {int(self.thymio.x)}, Y: {int(self.thymio.y)}")
        self.angle_label.setText(f"Angle: {int(self.thymio.angle)}°")

        # LEDs
        r, g, b = self.thymio.leds.top
        if r > 0 or g > 0 or b > 0:
            self.led_top_label.setText(f"LED: ({r},{g},{b})")
            self.led_top_label.setStyleSheet(
                f"background-color: rgb({r*8}, {g*8}, {b*8}); padding: 2px;"
            )
        else:
            self.led_top_label.setText(self.tr("LED: Off"))
            self.led_top_label.setStyleSheet("")

        # Zoom info
        self.zoom_label.setText(self.tr("Zoom: {0}%").format(int(self.zoom_level * 100)))
        self.pan_label.setText(self.tr("Pan: {0}, {1}").format(int(self.camera_x), int(self.camera_y)))

    def _check_proximity_warnings(self):
        """Check for proximity warnings and update status bar"""
        front_center = self.thymio.sensors.proximity[2]
        if front_center > 3000:
            self.statusbar.showMessage(self.tr("Warning: Obstacle very close!"))
        elif front_center > 2000:
            self.statusbar.showMessage(self.tr("Obstacle detected ahead"))

    def toggle_sensors(self):
        """Toggle sensor visualization"""
        self.renderer.toggle_sensors()
        state = self.tr("on") if self.renderer.show_sensors else self.tr("off")
        self.statusbar.showMessage(self.tr("Sensor visualization: {0}").format(state))
