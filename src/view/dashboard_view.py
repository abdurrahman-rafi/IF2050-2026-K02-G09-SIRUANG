from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.controller.fasilitas_controller import FasilitasController
    from src.controller.laporan_controller import LaporanController
    from src.controller.reservasi_controller import ReservasiController
    from src.controller.warga_controller import WargaController


class DashboardView(QWidget):
    """Halaman utama dashboard dengan statistik ringkasan sistem."""

    def __init__(
        self,
        warga_controller: WargaController,
        fasilitas_controller: FasilitasController,
        reservasi_controller: ReservasiController,
        laporan_controller: LaporanController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._warga_ctrl = warga_controller
        self._fasilitas_ctrl = fasilitas_controller
        self._reservasi_ctrl = reservasi_controller
        self._laporan_ctrl = laporan_controller
        self._setup_ui()

    # ------------------------------------------------------------------ #
    # Setup UI                                                             #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(28)

        # Judul halaman
        header = QLabel("Dashboard")
        header.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        layout.addWidget(header)

        # Baris kartu statistik
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        for kartu in self._buat_semua_stat_card():
            cards_row.addWidget(kartu)
        layout.addLayout(cards_row)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------ #
    # Pengambilan data                                                     #
    # ------------------------------------------------------------------ #

    def _ambil_stats(self) -> Tuple[int, int, int, Decimal]:
        today = date.today()

        try:
            semua_reservasi = self._reservasi_ctrl.lihat_daftar_reservasi()
        except Exception:
            semua_reservasi = []

        try:
            total_warga = len(self._warga_ctrl.lihat_daftar_warga())
        except Exception:
            total_warga = 0

        try:
            total_fasilitas = len(self._fasilitas_ctrl.lihat_daftar_fasilitas())
        except Exception:
            total_fasilitas = 0

        reservasi_hari_ini = [r for r in semua_reservasi if r.tanggal_dibuat == today]

        first_of_month = today.replace(day=1)
        if today.month == 12:
            last_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        reservasi_bulan = [
            r for r in semua_reservasi
            if first_of_month <= r.tanggal_dibuat <= last_of_month
        ]

        try:
            pendapatan = self._laporan_ctrl.hitung_total_pendapatan(reservasi_bulan)
        except Exception:
            pendapatan = Decimal("0")

        return total_warga, total_fasilitas, len(reservasi_hari_ini), pendapatan

    # ------------------------------------------------------------------ #
    # Pembuat kartu                                                        #
    # ------------------------------------------------------------------ #

    def _buat_semua_stat_card(self) -> List[QFrame]:
        total_warga, total_fasilitas, reservasi_hari_ini, pendapatan = self._ambil_stats()
        pendapatan_str = "Rp " + f"{int(pendapatan):,}".replace(",", ".")

        configs = [
            ("Total Warga",         str(total_warga),          "#4182fa", "#eef4ff"),
            ("Total Fasilitas",     str(total_fasilitas),      "#22c55e", "#dcfce7"),
            ("Reservasi Hari Ini",  str(reservasi_hari_ini),   "#f59e0b", "#fef3c7"),
            ("Pendapatan Bulan Ini", pendapatan_str,           "#a855f7", "#f3e8ff"),
        ]
        return [self._buat_stat_card(*cfg) for cfg in configs]

    def _buat_stat_card(
        self, judul: str, nilai: str, warna_aksen: str, warna_bg: str
    ) -> QFrame:
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setStyleSheet(
            "QFrame#statCard {"
            "  background: #ffffff;"
            "  border-radius: 12px;"
            "  border: 1px solid #e2e8f0;"
            "}"
        )

        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 18))
        frame.setGraphicsEffect(shadow)

        row = QHBoxLayout(frame)
        row.setContentsMargins(20, 18, 20, 18)
        row.setSpacing(16)

        # Kotak ikon berwarna
        icon_box = QFrame()
        icon_box.setFixedSize(52, 52)
        icon_box.setStyleSheet(
            f"background: {warna_bg}; border-radius: 12px; border: none;"
        )
        dot = QLabel("●")
        dot.setStyleSheet(
            f"color: {warna_aksen}; font-size: 22px; background: transparent; border: none;"
        )
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib_layout = QVBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        ib_layout.addWidget(dot)

        # Teks nilai dan judul
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        lbl_nilai = QLabel(nilai)
        lbl_nilai.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #1a1a2e;"
            " background: transparent; border: none;"
        )

        lbl_judul = QLabel(judul)
        lbl_judul.setStyleSheet(
            "font-size: 12px; color: #64748b; background: transparent; border: none;"
        )

        text_col.addWidget(lbl_nilai)
        text_col.addWidget(lbl_judul)

        row.addWidget(icon_box)
        row.addLayout(text_col)
        row.addStretch()

        return frame
