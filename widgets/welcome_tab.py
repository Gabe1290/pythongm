#!/usr/bin/env python3
"""
Welcome Tab Widget for PyGameMaker IDE.

Shown when no editors are open. Two-column layout:
  - Left:  "Get started" (new / open / import) + "Try a sample"
  - Right: "Continue where you left off" (inline recent-projects list)

Styling stays palette-driven so the user's selected theme (dark / light /
default) is respected. Sample-project buttons import the bundled .gmk
files into a user-chosen output folder so the original samples are not
modified.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from core.logger import get_logger
from utils.config import Config

logger = get_logger(__name__)

# Repo-root candidates that the Welcome tab can offer as starting points.
# (filename relative to repo root, display label).
SAMPLE_PROJECTS: List[Tuple[str, str]] = [
    ("maze_1.gmk", "Maze — Level 1"),
    ("maze_2.gmk", "Maze — Level 2"),
    ("maze_3.gmk", "Maze — Level 3"),
    ("maze_4.gmk", "Maze — Level 4"),
    ("treasure.gmk", "Treasure hunt"),
]


def _format_mtime(path: Path) -> str:
    """Human-friendly modification-time string. Falls back to '—' if the
    file is missing or stat fails.
    """
    try:
        delta = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return "—"
    days = delta.days
    if days < 1:
        hours = int(delta.total_seconds() // 3600)
        if hours < 1:
            return "just now"
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


class WelcomeTab(QWidget):
    """Welcome tab shown when no editors are open."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        # The recent-projects QListWidget is stored on self so
        # refresh_recent_projects() can rebuild it without recreating
        # the whole tab.
        self._recent_list = None
        self._setup_ui()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 32, 40, 16)
        outer.setSpacing(16)

        # --- Header ---
        title = QLabel(self.tr("Welcome to PyGameMaker IDE"))
        title.setAlignment(Qt.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        outer.addWidget(title)

        version_label = QLabel(self._version_string())
        version_label.setAlignment(Qt.AlignCenter)
        version_font = version_label.font()
        version_font.setPointSize(10)
        version_label.setFont(version_font)
        # Use the standard "disabled / muted" palette role so this dims
        # automatically in dark themes without us hardcoding a hex colour.
        version_label.setObjectName("welcomeVersionLabel")
        outer.addWidget(version_label)

        outer.addSpacing(8)

        # --- Two-column body ---
        body = QHBoxLayout()
        body.setSpacing(24)
        body.addWidget(self._build_left_column(), 1)
        body.addWidget(self._build_right_column(), 1)
        outer.addLayout(body, 1)

        # --- Footer links ---
        outer.addWidget(self._build_footer())

    def _build_left_column(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMinimumWidth(280)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(8)

        lay.addWidget(self._section_heading(self.tr("Get started")))

        # Two primary actions remain visible buttons …
        lay.addWidget(self._action_button(
            self.tr("📄  New Project"), "Ctrl+N", self._on_new_project))
        lay.addWidget(self._action_button(
            self.tr("📂  Open Project..."), "Ctrl+O", self._on_open_project))

        # … the rest fold into a single "More options" dropdown so the
        # column doesn't visually shout six choices at every new user.
        lay.addWidget(self._dropdown_button(
            self.tr("More options"),
            [
                (self.tr("🗜  Open ZIP Project..."),         self._on_open_zip),
                (self.tr("📥  Import GameMaker .gmk..."),    self._on_import_gmk),
                (self.tr("📥  Import Open Roberta XML..."),  self._on_import_roberta),
            ],
        ))

        lay.addSpacing(12)
        lay.addWidget(self._section_heading(self.tr("Try a sample game")))

        # Sample games are also a dropdown — five vertical buttons made the
        # Welcome tab feel overstuffed (user feedback after first revision).
        repo_root = self._repo_root()
        sample_items = []
        for filename, label in SAMPLE_PROJECTS:
            sample = repo_root / filename
            if not sample.exists():
                continue  # missing in this checkout — skip silently
            sample_items.append((
                self.tr("🎮  {0}").format(label),
                lambda _checked=False, p=sample: self._on_open_sample(p),
            ))

        if sample_items:
            lay.addWidget(self._dropdown_button(
                self.tr("Choose a sample"), sample_items))
        else:
            placeholder = QLabel(self.tr("(No bundled samples found in this build.)"))
            placeholder.setObjectName("welcomeMutedLabel")
            lay.addWidget(placeholder)

        lay.addStretch(1)
        return frame

    def _build_right_column(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMinimumWidth(280)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(8)

        lay.addWidget(self._section_heading(self.tr("Continue where you left off")))

        # QListWidget gives us the "clear list format" look the user asked
        # for: native single-line rows, built-in hover + selection highlight,
        # scrollbar when the list grows, all theme-aware out of the box.
        self._recent_list = QListWidget()
        self._recent_list.setFrameShape(QFrame.NoFrame)
        self._recent_list.setUniformItemSizes(True)
        self._recent_list.setMouseTracking(True)
        self._recent_list.setCursor(Qt.PointingHandCursor)
        self._recent_list.itemActivated.connect(self._on_recent_item_clicked)
        self._recent_list.itemClicked.connect(self._on_recent_item_clicked)
        lay.addWidget(self._recent_list, 1)
        self._populate_recent_list()

        # Clear-recent sits at the bottom-right and hides itself when the
        # list is empty so an empty panel stays uncluttered.
        self._clear_recent_btn = QPushButton(self.tr("Clear recent projects"))
        self._clear_recent_btn.setFlat(True)
        self._clear_recent_btn.clicked.connect(self._on_clear_recent)
        lay.addWidget(self._clear_recent_btn, 0, Qt.AlignRight)
        self._clear_recent_btn.setVisible(bool(Config.get("recent_projects", [])))
        return frame

    def _build_footer(self) -> QWidget:
        host = QWidget()
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch(1)
        for label, slot in (
            (self.tr("Documentation"), self._on_show_docs),
            (self.tr("Tutorials"),     self._on_show_tutorials),
            (self.tr("About"),         self._on_show_about),
        ):
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        return host

    # ------------------------------------------------------------------
    # Recent-projects list (rebuilt on demand)
    # ------------------------------------------------------------------

    def _populate_recent_list(self):
        """Fill self._recent_list (QListWidget) with the recent projects.

        Each entry is a QListWidgetItem hosting a small two-label widget
        (project name on the left, mtime on the right). Stored as a custom
        widget instead of plain item text so the mtime can be right-aligned
        and visually de-emphasised without parsing the row text later.
        """
        if not hasattr(self, '_recent_list') or self._recent_list is None:
            return
        self._recent_list.clear()

        recent = Config.get("recent_projects", []) or []
        if not recent:
            placeholder = QListWidgetItem(self.tr("(No recent projects yet.)"))
            placeholder.setFlags(Qt.NoItemFlags)
            self._recent_list.addItem(placeholder)
            return

        for project_path in recent[:8]:
            item = QListWidgetItem(self._recent_list)
            item.setData(Qt.UserRole, project_path)
            item.setToolTip(project_path)
            row_widget = self._recent_row_widget(project_path)
            # Lock the item's height to the row's preferred height so
            # uniformItemSizes can keep painting fast.
            item.setSizeHint(row_widget.sizeHint())
            self._recent_list.setItemWidget(item, row_widget)

    def _recent_row_widget(self, project_path: str) -> QWidget:
        """Build the per-row widget for the recent-projects list.

        Two labels in a tight horizontal layout. No button styling — the
        QListWidget itself owns hover / selection highlighting via the
        active theme palette.
        """
        path = Path(project_path)
        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(8, 3, 8, 3)
        row_lay.setSpacing(8)

        name_label = QLabel(path.name)
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row_lay.addWidget(name_label, 1)

        mtime = _format_mtime(path)
        if mtime and mtime != "—":
            # Don't render anything when we can't read the mtime — an
            # em-dash placeholder reads as broken data in a clean list.
            time_label = QLabel(mtime)
            time_label.setObjectName("welcomeMutedLabel")
            time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            f = time_label.font()
            f.setPointSizeF(max(f.pointSizeF() - 1, 8.0))
            time_label.setFont(f)
            row_lay.addWidget(time_label, 0, Qt.AlignRight | Qt.AlignVCenter)
        return row

    def _on_recent_item_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole) if item else None
        if path:
            self._on_open_recent(path)

    def refresh_recent_projects(self):
        """Public hook for the IDE to call after recent-projects changes
        (open / clear). Rebuilds only the right-column list.
        """
        self._populate_recent_list()
        if hasattr(self, '_clear_recent_btn'):
            self._clear_recent_btn.setVisible(bool(Config.get("recent_projects", [])))

    # ------------------------------------------------------------------
    # Small UI helpers
    # ------------------------------------------------------------------

    def _section_heading(self, text: str) -> QLabel:
        label = QLabel(text)
        f = label.font()
        f.setBold(True)
        f.setPointSize(f.pointSize() + 1)
        label.setFont(f)
        return label

    def _action_button(self, label: str, shortcut, slot) -> QPushButton:
        if shortcut:
            label = f"{label}\t{shortcut}"
        btn = QPushButton(label)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { text-align: left; padding: 8px 12px; }"
        )
        btn.clicked.connect(lambda _checked=False: slot())
        return btn

    def _dropdown_button(self, label: str, items) -> QPushButton:
        """Create a button that, when clicked, pops up a menu of choices.

        ``items`` is a list of ``(item_label, callable)`` pairs. The
        callable can accept either no args or a single ``checked`` arg
        (Qt signal signature). We use QPushButton.setMenu so the down-arrow
        indicator is rendered automatically by Qt.
        """
        btn = QPushButton(label)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { text-align: left; padding: 8px 12px; }"
        )
        menu = QMenu(btn)
        for item_label, slot in items:
            action = menu.addAction(item_label)
            action.triggered.connect(slot)
        btn.setMenu(menu)
        return btn

    def _repo_root(self) -> Path:
        """Locate the repo root that hosts the bundled sample .gmk files.

        widgets/welcome_tab.py is one level under the repo root, so the
        parent of this file's parent is the repo root. Cached on self
        only inside this method (computed each call is cheap).
        """
        return Path(__file__).resolve().parent.parent

    def _version_string(self) -> str:
        """Best-effort version label. Falls back to a placeholder so the
        UI never shows an empty version line.
        """
        try:
            from utils import __version__ as v
            return f"v{v}"
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Slots — delegate to the IDE main window where possible
    # ------------------------------------------------------------------

    def _on_new_project(self):
        if self.main_window and hasattr(self.main_window, 'new_project'):
            self.main_window.new_project()

    def _on_open_project(self):
        if self.main_window and hasattr(self.main_window, 'open_project'):
            self.main_window.open_project()

    def _on_open_zip(self):
        if self.main_window and hasattr(self.main_window, 'open_project_zip'):
            self.main_window.open_project_zip()

    def _on_import_gmk(self):
        if self.main_window and hasattr(self.main_window, 'import_gmk_file'):
            self.main_window.import_gmk_file()

    def _on_import_roberta(self):
        if self.main_window and hasattr(self.main_window, 'import_roberta_xml'):
            self.main_window.import_roberta_xml()

    def _on_open_recent(self, project_path: str):
        if self.main_window and hasattr(self.main_window, 'open_recent_project'):
            self.main_window.open_recent_project(project_path)

    def _on_clear_recent(self):
        if self.main_window and hasattr(self.main_window, 'clear_recent_projects'):
            self.main_window.clear_recent_projects()
            # IDE-level method may not call us back; refresh defensively.
            self.refresh_recent_projects()

    def _on_show_docs(self):
        if self.main_window and hasattr(self.main_window, 'show_documentation'):
            self.main_window.show_documentation()

    def _on_show_tutorials(self):
        if self.main_window and hasattr(self.main_window, 'show_tutorials'):
            self.main_window.show_tutorials()

    def _on_show_about(self):
        if self.main_window and hasattr(self.main_window, 'about'):
            self.main_window.about()

    def _on_open_sample(self, sample_path: Path):
        """Import a bundled sample .gmk into a user-chosen folder so the
        original sample is never modified, then open the result.
        """
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        if self.main_window is None:
            return
        # Default save location: <Documents>/PyGameMaker Projects/<sample-stem>
        from utils import documents_dir
        default_parent = documents_dir() / "PyGameMaker Projects"
        try:
            default_parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            default_parent = Path.home()
        default_output = str(default_parent / sample_path.stem)

        output_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Save sample project to..."),
            default_output,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if not output_dir:
            return

        try:
            from importers.gmk_importer import import_gmk_detailed
            result = import_gmk_detailed(str(sample_path), output_dir)
        except Exception as exc:
            logger.error(f"Sample import failed: {exc}", exc_info=True)
            QMessageBox.warning(
                self,
                self.tr("Sample import failed"),
                self.tr("Could not import the sample project:\n{0}").format(str(exc)),
            )
            return

        if not getattr(result, 'success', False):
            QMessageBox.warning(
                self,
                self.tr("Sample import failed"),
                self.tr("The bundled sample could not be imported. "
                        "See the console output for details."),
            )
            return

        # Open the freshly imported project
        project_file = Path(output_dir) / "project.json"
        if project_file.exists() and hasattr(self.main_window, 'load_project'):
            self.main_window.load_project(Path(output_dir))
