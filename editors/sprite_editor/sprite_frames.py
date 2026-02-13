#!/usr/bin/env python3
"""
Animation Frame Timeline for the Sprite Editor.
Displays frame thumbnails, allows add/remove/duplicate/reorder,
and provides animation preview playback.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QScrollArea, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QRect
from PySide6.QtGui import QImage, QPainter, QColor, QPixmap, QPen


_THUMB_SIZE = 64
_CHECKER_SIZE = 4
_CHECKER_LIGHT = QColor(204, 204, 204)
_CHECKER_DARK = QColor(170, 170, 170)


class FrameThumbnail(QWidget):
    """A clickable thumbnail representing one animation frame."""

    clicked = Signal(int)  # frame index

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.image = None  # QImage
        self.selected = False
        self.setFixedSize(_THUMB_SIZE + 4, _THUMB_SIZE + 20)

    def set_image(self, image: QImage):
        self.image = image
        self.update()

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background / selection highlight
        if self.selected:
            painter.fillRect(self.rect(), QColor(70, 130, 200))
        else:
            painter.fillRect(self.rect(), QColor(60, 60, 60))

        # Draw checkerboard inside thumbnail area
        tx, ty = 2, 2
        tw, th = _THUMB_SIZE, _THUMB_SIZE
        for r in range(tw // _CHECKER_SIZE + 1):
            for c in range(th // _CHECKER_SIZE + 1):
                color = _CHECKER_LIGHT if (r + c) % 2 == 0 else _CHECKER_DARK
                painter.fillRect(
                    tx + c * _CHECKER_SIZE, ty + r * _CHECKER_SIZE,
                    _CHECKER_SIZE, _CHECKER_SIZE, color
                )

        # Draw scaled image
        if self.image and not self.image.isNull():
            scaled = self.image.scaled(
                tw, th, Qt.KeepAspectRatio, Qt.FastTransformation
            )
            ix = tx + (tw - scaled.width()) // 2
            iy = ty + (th - scaled.height()) // 2
            painter.drawImage(ix, iy, scaled)

        # Border
        pen_color = QColor(100, 180, 255) if self.selected else QColor(100, 100, 100)
        painter.setPen(QPen(pen_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(tx, ty, tw, th)

        # Frame number label
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(0, _THUMB_SIZE + 4, _THUMB_SIZE + 4, 16),
                         Qt.AlignCenter, str(self.index + 1))

        painter.end()


class FrameTimeline(QWidget):
    """Horizontal frame timeline with thumbnails and animation controls."""

    frame_selected = Signal(int)   # index of selected frame
    frames_changed = Signal()      # emitted when frames are added/removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frames = []         # list of QImage
        self._current_index = 0
        self._thumbnails = []     # list of FrameThumbnail widgets
        self._fps = 10.0

        # Animation playback
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._anim_next_frame)
        self._playing = False

        self.setMaximumHeight(_THUMB_SIZE + 60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 2, 4, 2)
        main_layout.setSpacing(2)

        # Top row: buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        self._add_btn = QPushButton(self.tr("+"))
        self._add_btn.setToolTip(self.tr("Add frame"))
        self._add_btn.setFixedWidth(28)
        self._add_btn.clicked.connect(self.add_frame)

        self._dup_btn = QPushButton(self.tr("D"))
        self._dup_btn.setToolTip(self.tr("Duplicate frame"))
        self._dup_btn.setFixedWidth(28)
        self._dup_btn.clicked.connect(self.duplicate_frame)

        self._del_btn = QPushButton(self.tr("-"))
        self._del_btn.setToolTip(self.tr("Delete frame"))
        self._del_btn.setFixedWidth(28)
        self._del_btn.clicked.connect(self.delete_frame)

        self._play_btn = QPushButton(self.tr("Play"))
        self._play_btn.setFixedWidth(48)
        self._play_btn.clicked.connect(self._toggle_playback)

        self._frame_label = QLabel("1 / 1")
        self._frame_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._dup_btn)
        btn_layout.addWidget(self._del_btn)
        btn_layout.addSpacing(8)
        btn_layout.addWidget(self._play_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._frame_label)

        main_layout.addLayout(btn_layout)

        # Bottom row: scrollable thumbnail strip
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll_area.setFixedHeight(_THUMB_SIZE + 26)

        self._thumb_container = QWidget()
        self._thumb_layout = QHBoxLayout(self._thumb_container)
        self._thumb_layout.setContentsMargins(2, 2, 2, 2)
        self._thumb_layout.setSpacing(4)
        self._thumb_layout.addStretch()

        self._scroll_area.setWidget(self._thumb_container)
        main_layout.addWidget(self._scroll_area)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_frames(self, frames: list):
        """Set the frame list (list of QImage)."""
        self._frames = list(frames) if frames else []
        if not self._frames:
            # Always have at least one blank frame
            blank = QImage(32, 32, QImage.Format_ARGB32)
            blank.fill(QColor(0, 0, 0, 0))
            self._frames.append(blank)
        self._current_index = 0
        self._rebuild_thumbnails()
        self._update_selection()

    def get_frames(self) -> list:
        """Return list of QImage frames."""
        return list(self._frames)

    def get_current_frame(self) -> QImage:
        if 0 <= self._current_index < len(self._frames):
            return self._frames[self._current_index]
        return self._frames[0] if self._frames else None

    def get_current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int):
        if 0 <= index < len(self._frames):
            self._current_index = index
            self._update_selection()
            self.frame_selected.emit(index)

    def update_current_frame(self, image: QImage):
        """Replace the current frame's image (after drawing)."""
        if 0 <= self._current_index < len(self._frames):
            self._frames[self._current_index] = image.copy()
            if self._current_index < len(self._thumbnails):
                self._thumbnails[self._current_index].set_image(image)

    def set_fps(self, fps: float):
        self._fps = max(0.1, fps)
        if self._playing:
            self._anim_timer.setInterval(int(1000 / self._fps))

    def get_frame_count(self) -> int:
        return len(self._frames)

    def get_frame_size(self) -> tuple:
        """Return (width, height) of the first frame."""
        if self._frames:
            return self._frames[0].width(), self._frames[0].height()
        return 32, 32

    # ------------------------------------------------------------------
    # Frame operations
    # ------------------------------------------------------------------

    def add_frame(self):
        """Add a new blank frame after the current one."""
        w, h = self.get_frame_size()
        blank = QImage(w, h, QImage.Format_ARGB32)
        blank.fill(QColor(0, 0, 0, 0))
        insert_at = self._current_index + 1
        self._frames.insert(insert_at, blank)
        self._rebuild_thumbnails()
        self.set_current_index(insert_at)
        self.frames_changed.emit()

    def duplicate_frame(self):
        """Duplicate the current frame."""
        if not self._frames:
            return
        copy = self._frames[self._current_index].copy()
        insert_at = self._current_index + 1
        self._frames.insert(insert_at, copy)
        self._rebuild_thumbnails()
        self.set_current_index(insert_at)
        self.frames_changed.emit()

    def delete_frame(self):
        """Delete the current frame (keep at least one)."""
        if len(self._frames) <= 1:
            return
        del self._frames[self._current_index]
        if self._current_index >= len(self._frames):
            self._current_index = len(self._frames) - 1
        self._rebuild_thumbnails()
        self._update_selection()
        self.frame_selected.emit(self._current_index)
        self.frames_changed.emit()

    # ------------------------------------------------------------------
    # Compositing — assemble frames into a horizontal strip PNG
    # ------------------------------------------------------------------

    def composite_strip(self) -> QImage:
        """Composite all frames into a single horizontal strip image."""
        if not self._frames:
            return QImage(32, 32, QImage.Format_ARGB32)

        w, h = self.get_frame_size()
        n = len(self._frames)
        strip = QImage(w * n, h, QImage.Format_ARGB32)
        strip.fill(QColor(0, 0, 0, 0))

        painter = QPainter(strip)
        for i, frame in enumerate(self._frames):
            painter.drawImage(i * w, 0, frame)
        painter.end()

        return strip

    # ------------------------------------------------------------------
    # Animation playback
    # ------------------------------------------------------------------

    def _toggle_playback(self):
        if self._playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        if len(self._frames) <= 1:
            return
        self._playing = True
        self._play_btn.setText(self.tr("Stop"))
        self._anim_timer.start(int(1000 / self._fps))

    def stop_playback(self):
        self._playing = False
        self._play_btn.setText(self.tr("Play"))
        self._anim_timer.stop()

    def _anim_next_frame(self):
        next_idx = (self._current_index + 1) % len(self._frames)
        self.set_current_index(next_idx)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild_thumbnails(self):
        """Rebuild all thumbnail widgets from self._frames."""
        # Remove old thumbnails
        for thumb in self._thumbnails:
            self._thumb_layout.removeWidget(thumb)
            thumb.deleteLater()
        self._thumbnails.clear()

        # Remove stretch
        while self._thumb_layout.count():
            item = self._thumb_layout.takeAt(0)

        # Add new thumbnails
        for i, frame in enumerate(self._frames):
            thumb = FrameThumbnail(i, self._thumb_container)
            thumb.set_image(frame)
            thumb.clicked.connect(self._on_thumb_clicked)
            self._thumb_layout.addWidget(thumb)
            self._thumbnails.append(thumb)

        self._thumb_layout.addStretch()
        self._update_label()

    def _update_selection(self):
        for i, thumb in enumerate(self._thumbnails):
            thumb.set_selected(i == self._current_index)
        self._update_label()

    def _update_label(self):
        self._frame_label.setText(f"{self._current_index + 1} / {len(self._frames)}")

    def _on_thumb_clicked(self, index: int):
        if self._playing:
            self.stop_playback()
        self.set_current_index(index)
