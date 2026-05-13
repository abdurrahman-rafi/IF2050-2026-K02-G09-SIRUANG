from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.view.dashboard_view import DashboardView
from src.view.fasilitas_view import FasilitasView
from src.view.laporan_view import LaporanView
from src.view.notifikasi_view import NotifikasiView
from src.view.warga_view import WargaView

if TYPE_CHECKING:
    from src.controller.fasilitas_controller import FasilitasController
    from src.controller.laporan_controller import LaporanController
    from src.controller.notifikasi_controller import NotifikasiController
    from src.controller.reservasi_controller import ReservasiController
    from src.controller.warga_controller import WargaController
    from src.data.data_repository import DataRepository


# ------------------------------------------------------------------ #
# Design tokens                                                        #
# ------------------------------------------------------------------ #

GLOBAL_STYLE = """
QWidget {
    font-family: 'Hanken Grotesk', 'Ubuntu', 'Cantarell', 'DejaVu Sans', sans-serif;
    font-size: 13px;
    color: #1a1a2e;
}
QMainWindow, QScrollArea > QWidget > QWidget {
    background-color: #f4f4f4;
}
QScrollArea {
    background-color: #f4f4f4;
    border: none;
}
QDialog {
    background-color: #ffffff;
}

/* --- Tombol utama --- */
QPushButton {
    background-color: #003773;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 7px 18px;
    font-weight: 600;
    min-height: 32px;
}
QPushButton:hover  { background-color: #002555; }
QPushButton:pressed { background-color: #001f40; }

QPushButton[flat="true"] {
    background-color: transparent;
    color: #1a1a2e;
    border: none;
    min-height: 0;
}
QPushButton[outline="true"] {
    background-color: transparent;
    color: #003773;
    border: 1.5px solid #003773;
}
QPushButton[outline="true"]:hover { background-color: #eef4ff; }

QPushButton[danger="true"] {
    background-color: #ef4444;
    color: white;
}
QPushButton[danger="true"]:hover { background-color: #dc2626; }

/* --- Tombol navbar --- */
QPushButton[nav="true"] {
    background-color: transparent;
    color: rgba(255,255,255,0.75);
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    min-height: 28px;
}
QPushButton[nav="true"]:hover {
    background-color: rgba(255,255,255,0.12);
    color: #ffffff;
}
QPushButton[nav="active"] {
    background-color: rgba(255,255,255,0.18);
    color: #ffffff;
    font-weight: 700;
}

/* --- Input --- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: #4182fa;
}
QLineEdit:focus, QTextEdit:focus { border-color: #4182fa; }

QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QSpinBox {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 5px 10px;
    min-height: 30px;
}
QComboBox:focus, QDateEdit:focus, QTimeEdit:focus { border-color: #4182fa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow { width: 12px; height: 12px; }

/* --- Tabel --- */
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f0f4f8;
    alternate-background-color: #f8fafc;
}
QHeaderView::section {
    background-color: #003773;
    color: #ffffff;
    font-weight: 600;
    padding: 9px 8px;
    border: none;
    border-right: 1px solid #002a5a;
}
QHeaderView::section:last { border-right: none; }
QTableWidget::item { padding: 6px 8px; }
QTableWidget::item:selected {
    background-color: #eef4ff;
    color: #1a1a2e;
}

/* --- Dialog --- */
QDialogButtonBox QPushButton { min-width: 80px; }

/* --- Scrollbar --- */
QScrollBar:vertical {
    background: #f4f4f4;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #f4f4f4;
    height: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #94a3b8; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

_PAGE_DASHBOARD  = 0
_PAGE_FASILITAS  = 1
_PAGE_WARGA      = 2
_PAGE_LAPORAN    = 3


class MainWindow(QMainWindow):
    """Window utama aplikasi SIRUANG: navbar tetap dan routing antar halaman."""

    def __init__(
        self,
        warga_controller: WargaController,
        fasilitas_controller: FasilitasController,
        reservasi_controller: ReservasiController,
        laporan_controller: LaporanController,
        notifikasi_controller: NotifikasiController,
        data_repository: DataRepository,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._warga_ctrl = warga_controller
        self._fasilitas_ctrl = fasilitas_controller
        self._reservasi_ctrl = reservasi_controller
        self._laporan_ctrl = laporan_controller
        self._notifikasi_ctrl = notifikasi_controller
        self._data_repository = data_repository

        self._nav_buttons: Dict[str, QPushButton] = {}
        self._stack: Optional[QStackedWidget] = None
        self._notifikasi_view: Optional[NotifikasiView] = None

        QApplication.instance().setStyleSheet(GLOBAL_STYLE)
        self.setup_ui()

    # ------------------------------------------------------------------ #
    # Setup UI                                                             #
    # ------------------------------------------------------------------ #

    def setup_ui(self) -> None:
        """Menyiapkan tampilan awal window utama: navbar, area konten, dan judul aplikasi."""
        self.setWindowTitle("SIRUANG — Sistem Reservasi Fasilitas")
        self.setMinimumSize(1200, 720)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._buat_navbar())

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentStack")
        self._isi_stack()
        root.addWidget(self._stack)

        self.navigasi_ke_fasilitas()

    def _buat_navbar(self) -> QFrame:
        navbar = QFrame()
        navbar.setObjectName("navbar")
        navbar.setFixedHeight(60)
        navbar.setStyleSheet("QFrame#navbar { background-color: #003773; }")
        navbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(navbar)
        layout.setContentsMargins(32, 0, 24, 0)
        layout.setSpacing(4)

        brand = QLabel("SIRUANG")
        brand.setStyleSheet(
            "color: #ffffff; font-size: 18px; font-weight: 700;"
            " letter-spacing: 1px; background: transparent;"
        )
        layout.addWidget(brand)
        layout.addStretch()

        nav_items = [
            ("Dashboard",  self.navigasi_ke_dashboard),
            ("Fasilitas",  self.navigasi_ke_fasilitas),
            ("Warga",      self.navigasi_ke_warga),
            ("Laporan",    self.navigasi_ke_laporan),
        ]
        for label, slot in nav_items:
            btn = QPushButton(label)
            btn.setProperty("nav", "true")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            self._nav_buttons[label] = btn
            layout.addWidget(btn)

        layout.addSpacing(12)

        self._notifikasi_view = NotifikasiView(self._notifikasi_ctrl, parent=self)
        notif_widget = self._notifikasi_view.create_navbar_icon()
        self._notifikasi_view.start_badge_pulse()
        layout.addWidget(notif_widget)

        return navbar

    def _isi_stack(self) -> None:
        self._stack.addWidget(
            DashboardView(
                self._warga_ctrl,
                self._fasilitas_ctrl,
                self._reservasi_ctrl,
                self._laporan_ctrl,
            )
        )
        self._stack.addWidget(FasilitasView(self._data_repository, self._reservasi_ctrl))
        self._stack.addWidget(WargaView(self._warga_ctrl, self._data_repository))
        self._stack.addWidget(
            LaporanView(self._laporan_ctrl, self._data_repository, self._reservasi_ctrl)
        )

    # ------------------------------------------------------------------ #
    # Navigasi                                                             #
    # ------------------------------------------------------------------ #

    def _navigasi_ke(self, label: str, page_index: int) -> None:
        if self._stack is None:
            return
        self._stack.setCurrentIndex(page_index)
        for key, btn in self._nav_buttons.items():
            btn.setProperty("nav", "active" if key == label else "true")
            btn.style().polish(btn)

    def navigasi_ke_dashboard(self) -> None:
        """Menampilkan halaman Dashboard sebagai konten utama."""
        self._navigasi_ke("Dashboard", _PAGE_DASHBOARD)

    def navigasi_ke_fasilitas(self) -> None:
        """Menampilkan halaman Daftar Fasilitas sebagai konten utama."""
        self._navigasi_ke("Fasilitas", _PAGE_FASILITAS)

    def navigasi_ke_warga(self) -> None:
        """Menampilkan halaman Daftar Warga sebagai konten utama."""
        fasilitas_page = self._stack.widget(_PAGE_WARGA)
        if isinstance(fasilitas_page, WargaView):
            fasilitas_page.tampilkan_daftar_warga()
        self._navigasi_ke("Warga", _PAGE_WARGA)

    def navigasi_ke_reservasi(self) -> None:
        """Alias ke navigasi_ke_laporan (Laporan adalah daftar reservasi)."""
        self.navigasi_ke_laporan()

    def navigasi_ke_laporan(self) -> None:
        """Menampilkan halaman Laporan Reservasi sebagai konten utama."""
        laporan_page = self._stack.widget(_PAGE_LAPORAN)
        if isinstance(laporan_page, LaporanView):
            laporan_page.muat_ulang()
        self._navigasi_ke("Laporan", _PAGE_LAPORAN)

    def navigasi_ke_notifikasi(self) -> None:
        """Menampilkan panel daftar notifikasi."""
        if self._notifikasi_view is not None:
            self._notifikasi_view._on_bell_clicked()

    def perbarui_badge_notifikasi(self, jumlah_unread: int) -> None:
        """Memperbarui badge angka unread count pada ikon lonceng di navbar.

        Parameter:
            jumlah_unread: Jumlah notifikasi yang belum dibaca.
        """
        if self._notifikasi_view is not None:
            self._notifikasi_view.update_badge()
