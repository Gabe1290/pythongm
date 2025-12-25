#!/usr/bin/env python3
"""
Sprite Strip Import Dialog for PyGameMaker IDE
Allows configuring sprite sheets/strips with frame detection
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QFormLayout, QComboBox, QWidget, QSizePolicy,
    QSlider
)
from PySide6.QtCore import Qt, QTimer, Signal, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PIL import Image


class SpritePreviewWidget(QWidget):
    """Widget to display sprite with frame grid overlay"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 1
        self.rows = 1
        self.current_frame = 0
        self.show_grid = True
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_image(self, image_path: str):
        """Load and display an image"""
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
            self.frame_width = self.pixmap.width()
            self.frame_height = self.pixmap.height()
            self.columns = 1
            self.rows = 1
        self.update()

    def set_frame_size(self, width: int, height: int):
        """Set the frame dimensions"""
        self.frame_width = max(1, width)
        self.frame_height = max(1, height)
        if self.pixmap and not self.pixmap.isNull():
            self.columns = max(1, self.pixmap.width() // self.frame_width)
            self.rows = max(1, self.pixmap.height() // self.frame_height)
        self.update()

    def set_grid(self, columns: int, rows: int):
        """Set the grid dimensions"""
        self.columns = max(1, columns)
        self.rows = max(1, rows)
        if self.pixmap and not self.pixmap.isNull():
            self.frame_width = self.pixmap.width() // self.columns
            self.frame_height = self.pixmap.height() // self.rows
        self.update()

    def set_current_frame(self, frame: int):
        """Set the current frame to highlight"""
        self.current_frame = frame
        self.update()

    def get_frame_count(self) -> int:
        """Get total number of frames"""
        return self.columns * self.rows

    def paintEvent(self, event):
        """Draw the sprite with grid overlay"""
        if not self.pixmap or self.pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate scaling to fit widget while maintaining aspect ratio
        widget_rect = self.rect()
        pixmap_size = self.pixmap.size()

        scale = min(
            widget_rect.width() / pixmap_size.width(),
            widget_rect.height() / pixmap_size.height()
        )

        scaled_width = int(pixmap_size.width() * scale)
        scaled_height = int(pixmap_size.height() * scale)

        # Center the image
        x_offset = (widget_rect.width() - scaled_width) // 2
        y_offset = (widget_rect.height() - scaled_height) // 2

        # Draw scaled pixmap
        target_rect = QRect(x_offset, y_offset, scaled_width, scaled_height)
        painter.drawPixmap(target_rect, self.pixmap)

        if self.show_grid and self.columns > 0 and self.rows > 0:
            # Draw grid lines
            cell_width = scaled_width / self.columns
            cell_height = scaled_height / self.rows

            # Highlight current frame
            if self.current_frame < self.get_frame_count():
                col = self.current_frame % self.columns
                row = self.current_frame // self.columns
                highlight_rect = QRect(
                    int(x_offset + col * cell_width),
                    int(y_offset + row * cell_height),
                    int(cell_width),
                    int(cell_height)
                )
                painter.fillRect(highlight_rect, QColor(255, 255, 0, 80))

            # Draw grid lines
            pen = QPen(QColor(255, 0, 0, 180))
            pen.setWidth(2)
            painter.setPen(pen)

            # Vertical lines
            for i in range(self.columns + 1):
                x = x_offset + int(i * cell_width)
                painter.drawLine(x, y_offset, x, y_offset + scaled_height)

            # Horizontal lines
            for i in range(self.rows + 1):
                y = y_offset + int(i * cell_height)
                painter.drawLine(x_offset, y, x_offset + scaled_width, y)

        painter.end()


class AnimationPreviewWidget(QLabel):
    """Widget to preview animation playback"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.setMinimumSize(64, 64)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #333; border: 1px solid #555;")

    def set_frames(self, image_path: str, frame_width: int, frame_height: int,
                   columns: int, rows: int):
        """Extract and set frames from sprite sheet"""
        self.frames = []
        try:
            img = Image.open(image_path)
            for row in range(rows):
                for col in range(columns):
                    x = col * frame_width
                    y = row * frame_height
                    if x + frame_width <= img.width and y + frame_height <= img.height:
                        frame = img.crop((x, y, x + frame_width, y + frame_height))
                        # Convert PIL Image to QPixmap
                        if frame.mode != 'RGBA':
                            frame = frame.convert('RGBA')
                        data = frame.tobytes('raw', 'RGBA')
                        qimg = QImage(data, frame.width, frame.height,
                                     QImage.Format_RGBA8888)
                        self.frames.append(QPixmap.fromImage(qimg))
            img.close()
        except Exception as e:
            print(f"Error loading frames: {e}")

        self.current_frame = 0
        if self.frames:
            self.show_frame(0)

    def show_frame(self, index: int):
        """Display a specific frame"""
        if 0 <= index < len(self.frames):
            # Scale to fit with max size of 128x128
            pixmap = self.frames[index]
            scaled = pixmap.scaled(128, 128, Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation)
            self.setPixmap(scaled)

    def next_frame(self):
        """Advance to next frame"""
        if self.frames:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.show_frame(self.current_frame)

    def play(self, fps: float):
        """Start animation at given FPS"""
        if fps > 0 and self.frames:
            self.timer.start(int(1000 / fps))

    def stop(self):
        """Stop animation"""
        self.timer.stop()


class SpriteStripDialog(QDialog):
    """Dialog for configuring sprite strip/sheet import"""

    # Signal emitted when configuration is accepted
    configurationAccepted = Signal(dict)

    def __init__(self, image_path: str, sprite_name: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.sprite_name = sprite_name
        self.setWindowTitle(self.tr("Configure Sprite Strip"))
        self.setModal(True)
        self.resize(700, 550)
        self.setup_ui()
        self.load_image()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QHBoxLayout(self)

        # Left side: Preview
        left_panel = QVBoxLayout()

        preview_group = QGroupBox(self.tr("Sprite Sheet Preview"))
        preview_layout = QVBoxLayout(preview_group)

        self.sprite_preview = SpritePreviewWidget()
        preview_layout.addWidget(self.sprite_preview)

        # Frame slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel(self.tr("Frame:")))
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.valueChanged.connect(self.on_frame_changed)
        slider_layout.addWidget(self.frame_slider)
        self.frame_label = QLabel("0")
        slider_layout.addWidget(self.frame_label)
        preview_layout.addLayout(slider_layout)

        left_panel.addWidget(preview_group)

        # Animation preview
        anim_group = QGroupBox(self.tr("Animation Preview"))
        anim_layout = QVBoxLayout(anim_group)

        self.anim_preview = AnimationPreviewWidget()
        anim_layout.addWidget(self.anim_preview, alignment=Qt.AlignCenter)

        anim_buttons = QHBoxLayout()
        self.play_btn = QPushButton(self.tr("Play"))
        self.play_btn.clicked.connect(self.play_animation)
        self.stop_btn = QPushButton(self.tr("Stop"))
        self.stop_btn.clicked.connect(self.stop_animation)
        anim_buttons.addWidget(self.play_btn)
        anim_buttons.addWidget(self.stop_btn)
        anim_layout.addLayout(anim_buttons)

        left_panel.addWidget(anim_group)
        layout.addLayout(left_panel, stretch=2)

        # Right side: Configuration
        right_panel = QVBoxLayout()

        # Image info
        info_group = QGroupBox(self.tr("Image Info"))
        info_layout = QFormLayout(info_group)
        self.img_width_label = QLabel("0")
        self.img_height_label = QLabel("0")
        info_layout.addRow(self.tr("Width:"), self.img_width_label)
        info_layout.addRow(self.tr("Height:"), self.img_height_label)
        right_panel.addWidget(info_group)

        # Frame configuration
        frame_group = QGroupBox(self.tr("Frame Configuration"))
        frame_layout = QFormLayout(frame_group)

        # Strip type
        self.strip_type = QComboBox()
        self.strip_type.addItem(self.tr("Horizontal Strip"), "strip_h")
        self.strip_type.addItem(self.tr("Vertical Strip"), "strip_v")
        self.strip_type.addItem(self.tr("Grid (Rows x Columns)"), "grid")
        self.strip_type.currentIndexChanged.connect(self.on_strip_type_changed)
        frame_layout.addRow(self.tr("Strip Type:"), self.strip_type)

        # Frame dimensions
        self.frame_width_spin = QSpinBox()
        self.frame_width_spin.setRange(1, 4096)
        self.frame_width_spin.setValue(32)
        self.frame_width_spin.valueChanged.connect(self.on_frame_size_changed)
        frame_layout.addRow(self.tr("Frame Width:"), self.frame_width_spin)

        self.frame_height_spin = QSpinBox()
        self.frame_height_spin.setRange(1, 4096)
        self.frame_height_spin.setValue(32)
        self.frame_height_spin.valueChanged.connect(self.on_frame_size_changed)
        frame_layout.addRow(self.tr("Frame Height:"), self.frame_height_spin)

        # Columns/Rows
        self.columns_spin = QSpinBox()
        self.columns_spin.setRange(1, 100)
        self.columns_spin.setValue(1)
        self.columns_spin.valueChanged.connect(self.on_grid_changed)
        frame_layout.addRow(self.tr("Columns:"), self.columns_spin)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 100)
        self.rows_spin.setValue(1)
        self.rows_spin.valueChanged.connect(self.on_grid_changed)
        frame_layout.addRow(self.tr("Rows:"), self.rows_spin)

        # Frame count (read-only)
        self.frame_count_label = QLabel("1")
        frame_layout.addRow(self.tr("Total Frames:"), self.frame_count_label)

        right_panel.addWidget(frame_group)

        # Animation settings
        anim_settings_group = QGroupBox(self.tr("Animation Settings"))
        anim_settings_layout = QFormLayout(anim_settings_group)

        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 60.0)
        self.speed_spin.setValue(10.0)
        self.speed_spin.setSuffix(" FPS")
        self.speed_spin.setDecimals(1)
        anim_settings_layout.addRow(self.tr("Animation Speed:"), self.speed_spin)

        right_panel.addWidget(anim_settings_group)

        right_panel.addStretch()

        # Dialog buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton(self.tr("OK"))
        ok_btn.clicked.connect(self.accept_config)
        ok_btn.setDefault(True)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        right_panel.addLayout(button_layout)

        layout.addLayout(right_panel, stretch=1)

    def load_image(self):
        """Load the image and set initial values"""
        self.sprite_preview.set_image(self.image_path)

        try:
            with Image.open(self.image_path) as img:
                width, height = img.size
                self.img_width_label.setText(str(width))
                self.img_height_label.setText(str(height))

                # Auto-detect if it's a horizontal strip (wider than tall)
                if width > height and width % height == 0:
                    # Likely horizontal strip
                    frames = width // height
                    self.frame_width_spin.setValue(height)
                    self.frame_height_spin.setValue(height)
                    self.columns_spin.setValue(frames)
                    self.rows_spin.setValue(1)
                    self.strip_type.setCurrentIndex(0)  # Horizontal
                elif height > width and height % width == 0:
                    # Likely vertical strip
                    frames = height // width
                    self.frame_width_spin.setValue(width)
                    self.frame_height_spin.setValue(width)
                    self.columns_spin.setValue(1)
                    self.rows_spin.setValue(frames)
                    self.strip_type.setCurrentIndex(1)  # Vertical
                else:
                    # Single frame or grid - use full dimensions
                    self.frame_width_spin.setValue(width)
                    self.frame_height_spin.setValue(height)
                    self.columns_spin.setValue(1)
                    self.rows_spin.setValue(1)

        except Exception as e:
            print(f"Error loading image: {e}")

        self.update_preview()

    def on_strip_type_changed(self, index):
        """Handle strip type change"""
        strip_type = self.strip_type.currentData()
        # Enable/disable controls based on type
        self.columns_spin.setEnabled(strip_type in ("strip_h", "grid"))
        self.rows_spin.setEnabled(strip_type in ("strip_v", "grid"))

        if strip_type == "strip_h":
            self.rows_spin.setValue(1)
        elif strip_type == "strip_v":
            self.columns_spin.setValue(1)

        self.update_preview()

    def on_frame_size_changed(self):
        """Handle frame size change"""
        # Update columns/rows based on frame size
        try:
            with Image.open(self.image_path) as img:
                width, height = img.size
                frame_w = self.frame_width_spin.value()
                frame_h = self.frame_height_spin.value()

                if frame_w > 0 and frame_h > 0:
                    self.columns_spin.blockSignals(True)
                    self.rows_spin.blockSignals(True)
                    self.columns_spin.setValue(max(1, width // frame_w))
                    self.rows_spin.setValue(max(1, height // frame_h))
                    self.columns_spin.blockSignals(False)
                    self.rows_spin.blockSignals(False)
        except Exception:
            pass

        self.update_preview()

    def on_grid_changed(self):
        """Handle grid change"""
        # Update frame size based on grid
        try:
            with Image.open(self.image_path) as img:
                width, height = img.size
                cols = self.columns_spin.value()
                rows = self.rows_spin.value()

                if cols > 0 and rows > 0:
                    self.frame_width_spin.blockSignals(True)
                    self.frame_height_spin.blockSignals(True)
                    self.frame_width_spin.setValue(width // cols)
                    self.frame_height_spin.setValue(height // rows)
                    self.frame_width_spin.blockSignals(False)
                    self.frame_height_spin.blockSignals(False)
        except Exception:
            pass

        self.update_preview()

    def on_frame_changed(self, value):
        """Handle frame slider change"""
        self.frame_label.setText(str(value))
        self.sprite_preview.set_current_frame(value)

    def update_preview(self):
        """Update the preview widget"""
        frame_w = self.frame_width_spin.value()
        frame_h = self.frame_height_spin.value()
        cols = self.columns_spin.value()
        rows = self.rows_spin.value()

        self.sprite_preview.set_frame_size(frame_w, frame_h)
        frame_count = cols * rows
        self.frame_count_label.setText(str(frame_count))

        # Update slider range
        self.frame_slider.setMaximum(max(0, frame_count - 1))

        # Update animation preview
        self.anim_preview.set_frames(
            self.image_path, frame_w, frame_h, cols, rows
        )

    def play_animation(self):
        """Start animation preview"""
        fps = self.speed_spin.value()
        self.anim_preview.play(fps)

    def stop_animation(self):
        """Stop animation preview"""
        self.anim_preview.stop()

    def accept_config(self):
        """Accept the configuration and emit signal"""
        strip_type = self.strip_type.currentData()
        config = {
            "sprite_name": self.sprite_name,
            "image_path": self.image_path,
            "frames": self.columns_spin.value() * self.rows_spin.value(),
            "frame_width": self.frame_width_spin.value(),
            "frame_height": self.frame_height_spin.value(),
            "columns": self.columns_spin.value(),
            "rows": self.rows_spin.value(),
            "speed": self.speed_spin.value(),
            "animation_type": strip_type
        }
        self.configurationAccepted.emit(config)
        self.stop_animation()
        self.accept()

    def reject(self):
        """Handle dialog rejection"""
        self.stop_animation()
        super().reject()

    def get_configuration(self) -> dict:
        """Get the current configuration"""
        strip_type = self.strip_type.currentData()
        return {
            "sprite_name": self.sprite_name,
            "image_path": self.image_path,
            "frames": self.columns_spin.value() * self.rows_spin.value(),
            "frame_width": self.frame_width_spin.value(),
            "frame_height": self.frame_height_spin.value(),
            "columns": self.columns_spin.value(),
            "rows": self.rows_spin.value(),
            "speed": self.speed_spin.value(),
            "animation_type": strip_type
        }
