from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvas
    from matplotlib.ticker import FuncFormatter
    _MATPLOTLIB_OK = True
except ImportError:
    _MATPLOTLIB_OK = False

from src.entity.enums import StatusReservasi

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
        self._grafik_combo: Optional[QComboBox] = None
        self._grafik_canvas = None
        self._grafik_figure = None
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

        header = QLabel("Dashboard")
        header.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        layout.addWidget(header)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        for kartu in self._buat_semua_stat_card():
            cards_row.addWidget(kartu)
        layout.addLayout(cards_row)

        layout.addWidget(self._buat_kartu_grafik())
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
    # Pembuat kartu statistik                                              #
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

    # ------------------------------------------------------------------ #
    # Kartu grafik pendapatan bulanan                                      #
    # ------------------------------------------------------------------ #

    def _buat_kartu_grafik(self) -> QFrame:
        kartu = QFrame()
        kartu.setObjectName("grafikCard")
        kartu.setStyleSheet(
            "QFrame#grafikCard {"
            "  background: #ffffff;"
            "  border-radius: 12px;"
            "  border: 1px solid #e2e8f0;"
            "}"
        )
        shadow = QGraphicsDropShadowEffect(kartu)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 18))
        kartu.setGraphicsEffect(shadow)

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        lbl_judul = QLabel("Pendapatan Bulanan")
        lbl_judul.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        header_row.addWidget(lbl_judul)
        header_row.addStretch()

        self._grafik_combo = QComboBox()
        self._grafik_combo.setFixedHeight(32)
        self._grafik_combo.setMinimumWidth(170)
        self._grafik_combo.addItems(
            ["Bulan Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "1 Tahun Terakhir"]
        )
        header_row.addWidget(self._grafik_combo)
        layout.addLayout(header_row)

        if not _MATPLOTLIB_OK:
            lbl_err = QLabel("Grafik tidak tersedia — install matplotlib terlebih dahulu.")
            lbl_err.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
            lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_err.setMinimumHeight(180)
            layout.addWidget(lbl_err)
            return kartu

        self._grafik_figure = Figure(figsize=(10, 3), facecolor="#ffffff")
        self._grafik_canvas = FigureCanvas(self._grafik_figure)
        self._grafik_canvas.setMinimumHeight(220)
        layout.addWidget(self._grafik_canvas)

        self._grafik_combo.currentTextChanged.connect(self._perbarui_grafik)
        self._perbarui_grafik("Bulan Ini")

        return kartu

    def _perbarui_grafik(self, option: str) -> None:
        if not _MATPLOTLIB_OK or self._grafik_figure is None or self._grafik_canvas is None:
            return

        try:
            semua = self._reservasi_ctrl.lihat_daftar_reservasi()
        except Exception:
            semua = []

        lunas = [r for r in semua if getattr(r.status, "value", "") == StatusReservasi.LUNAS.value]

        today = date.today()
        if option == "Bulan Ini":
            data = self._kelompokkan_harian(lunas, today.year, today.month)
        elif option == "3 Bulan Terakhir":
            data = self._kelompokkan_bulanan(lunas, 3)
        elif option == "6 Bulan Terakhir":
            data = self._kelompokkan_bulanan(lunas, 6)
        else:
            data = self._kelompokkan_bulanan(lunas, 12)

        self._grafik_figure.clear()
        ax = self._grafik_figure.add_subplot(111)
        ax.set_facecolor("#ffffff")

        labels = [d[0] for d in data]
        values = [float(d[1]) for d in data]

        if not any(v > 0 for v in values):
            ax.text(
                0.5, 0.5, "Belum ada data pendapatan",
                ha="center", va="center", transform=ax.transAxes,
                color="#94a3b8", fontsize=12,
            )
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            x = list(range(len(labels)))
            ax.bar(x, values, color="#4182fa", width=0.6, zorder=2)

            ax.yaxis.grid(True, color="#f1f5f9", linewidth=0.8, zorder=1)
            ax.set_axisbelow(True)

            def _fmt_rp(val: float, _pos) -> str:
                if val >= 1_000_000:
                    return f"Rp {val / 1_000_000:.1f}jt"
                if val >= 1_000:
                    return f"Rp {val / 1_000:.0f}rb"
                return f"Rp {val:.0f}"

            ax.yaxis.set_major_formatter(FuncFormatter(_fmt_rp))

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#e2e8f0")
            ax.spines["bottom"].set_color("#e2e8f0")
            ax.tick_params(axis="both", colors="#64748b", labelsize=9)

            if option == "Bulan Ini" and len(labels) > 15:
                step = 5
                ax.set_xticks(x[::step])
                ax.set_xticklabels(labels[::step], fontsize=9)
            else:
                ax.set_xticks(x)
                ax.set_xticklabels(labels, fontsize=9)

        self._grafik_figure.tight_layout()
        self._grafik_canvas.draw()

    # ------------------------------------------------------------------ #
    # Helper pengelompokan data pendapatan                                 #
    # ------------------------------------------------------------------ #

    def _kelompokkan_harian(
        self, lunas_list, year: int, month: int
    ) -> List[Tuple[str, Decimal]]:
        _, days = calendar.monthrange(year, month)
        totals: dict[int, Decimal] = {d: Decimal("0") for d in range(1, days + 1)}
        for r in lunas_list:
            if (
                r.tanggal_dibuat
                and r.tanggal_dibuat.year == year
                and r.tanggal_dibuat.month == month
            ):
                totals[r.tanggal_dibuat.day] += r.total_biaya or Decimal("0")
        return [(str(d), totals[d]) for d in range(1, days + 1)]

    def _kelompokkan_bulanan(
        self, lunas_list, bulan_terakhir: int
    ) -> List[Tuple[str, Decimal]]:
        _BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                  "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        today = date.today()
        months: List[Tuple[int, int]] = []
        for i in range(bulan_terakhir - 1, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))

        totals: dict[Tuple[int, int], Decimal] = {k: Decimal("0") for k in months}
        for r in lunas_list:
            if r.tanggal_dibuat:
                key = (r.tanggal_dibuat.year, r.tanggal_dibuat.month)
                if key in totals:
                    totals[key] += r.total_biaya or Decimal("0")

        result = []
        for y, m in months:
            label = _BULAN[m - 1]
            if bulan_terakhir > 6:
                label += f" '{str(y)[2:]}"
            result.append((label, totals[(y, m)]))
        return result
