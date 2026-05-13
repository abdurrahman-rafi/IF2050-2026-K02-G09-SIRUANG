from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QGradient, QPainter
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.entity.enums import StatusReservasi

if TYPE_CHECKING:
    from src.controller.laporan_controller import LaporanController
    from src.data.data_repository import DataRepository
    from src.entity.reservasi import Reservasi


class LaporanView(QWidget):
    """Tampilan laporan riwayat transaksi dengan filter waktu dan fasilitas (UC12-UC13)."""

    def __init__(
        self,
        laporan_controller: LaporanController,
        data_repository: Optional[DataRepository] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._laporan_ctrl = laporan_controller
        self._data_repository = data_repository

        self._combo_fasilitas: Optional[QComboBox] = None
        self._input_dari: Optional[QDateEdit] = None
        self._input_sampai: Optional[QDateEdit] = None
        self._input_cari: Optional[QLabel] = None
        self._lbl_total: Optional[QLabel] = None
        self._lbl_jumlah: Optional[QLabel] = None
        self._tabel: Optional[QTableWidget] = None

        self._setup_ui()
        self._terapkan_filter()

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

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Judul
        header = QLabel("Laporan Reservasi")
        header.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        layout.addWidget(header)

        # Kartu filter
        layout.addWidget(self._buat_kartu_filter())

        # Kartu total pendapatan
        layout.addWidget(self._buat_kartu_pendapatan())

        # Tabel transaksi
        layout.addWidget(self._buat_tabel())

        scroll.setWidget(page)
        outer.addWidget(scroll)

    def _buat_kartu_filter(self) -> QFrame:
        kartu = QFrame()
        kartu.setObjectName("filterCard")
        kartu.setStyleSheet(
            "QFrame#filterCard {"
            "  background: #ffffff;"
            "  border-radius: 12px;"
            "  border: 1px solid #e2e8f0;"
            "}"
        )
        shadow = QGraphicsDropShadowEffect(kartu)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 14))
        kartu.setGraphicsEffect(shadow)

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        lbl = QLabel("Filter Laporan")
        lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #1a1a2e; background: transparent;")
        layout.addWidget(lbl)

        baris = QHBoxLayout()
        baris.setSpacing(10)

        # Filter fasilitas
        self._combo_fasilitas = QComboBox()
        self._combo_fasilitas.setFixedHeight(34)
        self._combo_fasilitas.setMinimumWidth(200)
        self._combo_fasilitas.addItem("Semua Fasilitas", None)
        if self._data_repository is not None:
            try:
                for f in self._data_repository.get_fasilitas_list():
                    self._combo_fasilitas.addItem(f.nama, f.id_fasilitas)
            except Exception:
                pass
        baris.addWidget(self._combo_fasilitas)

        # Tanggal dari
        lbl_dari = QLabel("Dari:")
        lbl_dari.setStyleSheet("color: #64748b; background: transparent;")
        lbl_dari.setFixedWidth(32)
        self._input_dari = QDateEdit(QDate.currentDate().addMonths(-1))
        self._input_dari.setCalendarPopup(True)
        self._input_dari.setFixedHeight(34)
        self._input_dari.setFixedWidth(130)
        baris.addWidget(lbl_dari)
        baris.addWidget(self._input_dari)

        # Tanggal sampai
        lbl_sampai = QLabel("Sampai:")
        lbl_sampai.setStyleSheet("color: #64748b; background: transparent;")
        lbl_sampai.setFixedWidth(52)
        self._input_sampai = QDateEdit(QDate.currentDate())
        self._input_sampai.setCalendarPopup(True)
        self._input_sampai.setFixedHeight(34)
        self._input_sampai.setFixedWidth(130)
        baris.addWidget(lbl_sampai)
        baris.addWidget(self._input_sampai)

        baris.addStretch()

        btn_filter = QPushButton("Tampilkan")
        btn_filter.setFixedHeight(34)
        btn_filter.setFixedWidth(110)
        btn_filter.clicked.connect(self._terapkan_filter)
        baris.addWidget(btn_filter)

        layout.addLayout(baris)
        return kartu

    def _buat_kartu_pendapatan(self) -> _GradientCard:
        kartu = _GradientCard()

        shadow = QGraphicsDropShadowEffect(kartu)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 55, 115, 60))
        kartu.setGraphicsEffect(shadow)

        layout = QVBoxLayout(kartu)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(6)

        lbl_judul = QLabel("Total Pendapatan (LUNAS)")
        lbl_judul.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 13px; background: transparent;")
        layout.addWidget(lbl_judul)

        self._lbl_total = QLabel("Rp 0")
        self._lbl_total.setStyleSheet(
            "color: #ffffff; font-size: 28px; font-weight: 700; background: transparent;"
        )
        layout.addWidget(self._lbl_total)

        self._lbl_jumlah = QLabel("dari 0 transaksi")
        self._lbl_jumlah.setStyleSheet(
            "color: rgba(255,255,255,0.75); font-size: 12px; background: transparent;"
        )
        layout.addWidget(self._lbl_jumlah)

        return kartu

    def _buat_tabel(self) -> QTableWidget:
        self._tabel = QTableWidget()
        self._tabel.setColumnCount(6)
        self._tabel.setHorizontalHeaderLabels(
            ["Warga", "Fasilitas", "Tanggal", "Jam", "Total Biaya", "Status"]
        )
        self._tabel.verticalHeader().setVisible(False)
        self._tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabel.setAlternatingRowColors(True)
        self._tabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        hdr = self._tabel.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        return self._tabel

    # ------------------------------------------------------------------ #
    # Logika filter & tampilan                                             #
    # ------------------------------------------------------------------ #

    def _terapkan_filter(self) -> None:
        id_fasilitas = self._combo_fasilitas.currentData() if self._combo_fasilitas else None
        dari = self._input_dari.date().toPyDate() if self._input_dari else date(2000, 1, 1)
        sampai = self._input_sampai.date().toPyDate() if self._input_sampai else date.today()

        try:
            if id_fasilitas is not None:
                hasil = self._laporan_ctrl.lihat_riwayat_per_fasilitas(id_fasilitas)
                hasil = [r for r in hasil if dari <= r.tanggal_dibuat <= sampai]
            else:
                hasil = self._laporan_ctrl.lihat_riwayat_per_waktu(dari, sampai)
        except Exception as e:
            self.tampilkan_pesan_error(f"Gagal memuat laporan: {e}")
            hasil = []

        try:
            total = self._laporan_ctrl.hitung_total_pendapatan(hasil)
        except Exception:
            total = Decimal("0")

        self._perbarui_kartu_pendapatan(total, len(hasil))
        self._isi_tabel(hasil)

    def _perbarui_kartu_pendapatan(self, total: Decimal, jumlah: int) -> None:
        if self._lbl_total is not None:
            total_str = "Rp " + f"{int(total):,}".replace(",", ".")
            self._lbl_total.setText(total_str)
        if self._lbl_jumlah is not None:
            self._lbl_jumlah.setText(f"dari {jumlah} transaksi")

    def _isi_tabel(self, daftar: List[Reservasi]) -> None:
        if self._tabel is None:
            return
        self._tabel.setRowCount(0)

        if not daftar:
            self._tabel.setRowCount(1)
            item = QTableWidgetItem("Tidak ada data untuk filter yang dipilih.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(0, 0, item)
            self._tabel.setSpan(0, 0, 1, 6)
            return

        self._tabel.setSpan(0, 0, 1, 1)
        self._tabel.setRowCount(len(daftar))

        for row, r in enumerate(daftar):
            nama_warga = self._resolve_nama_warga(r.id_warga)
            nama_fasilitas = self._resolve_nama_fasilitas(r.id_fasilitas)
            tanggal_str = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
            jam_str = (
                f"{r.jam_mulai.strftime('%H:%M')} – {r.jam_selesai.strftime('%H:%M')}"
                if r.jam_mulai and r.jam_selesai else "-"
            )
            biaya_str = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")

            self._tabel.setItem(row, 0, QTableWidgetItem(nama_warga))
            self._tabel.setItem(row, 1, QTableWidgetItem(nama_fasilitas))
            self._tabel.setItem(row, 2, QTableWidgetItem(tanggal_str))
            self._tabel.setItem(row, 3, QTableWidgetItem(jam_str))
            self._tabel.setItem(row, 4, QTableWidgetItem(biaya_str))

            if r.status == StatusReservasi.LUNAS:
                s_item = QTableWidgetItem("LUNAS")
                s_item.setForeground(QColor("#166534"))
                s_item.setBackground(QColor("#dcfce7"))
            else:
                s_item = QTableWidgetItem("BELUM DIBAYAR")
                s_item.setForeground(QColor("#92400e"))
                s_item.setBackground(QColor("#fef3c7"))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(row, 5, s_item)

    # ------------------------------------------------------------------ #
    # Metode publik (kontrak dari template)                                #
    # ------------------------------------------------------------------ #

    def tampilkan_laporan_per_waktu(
        self, list_reservasi: List[Reservasi], total_pendapatan: Decimal
    ) -> None:
        """Menampilkan laporan transaksi berdasarkan filter rentang waktu beserta
        card total pendapatan dan tabel 6-kolom riwayat transaksi.

        Parameter:
            list_reservasi: List Reservasi hasil filter rentang tanggal.
            total_pendapatan: Total pendapatan dari reservasi LUNAS dalam Decimal.
        """
        self._perbarui_kartu_pendapatan(total_pendapatan, len(list_reservasi))
        self._isi_tabel(list_reservasi)

    def tampilkan_laporan_per_fasilitas(
        self, list_reservasi: List[Reservasi], total_pendapatan: Decimal
    ) -> None:
        """Menampilkan laporan transaksi berdasarkan filter fasilitas beserta
        card total pendapatan dan tabel riwayat transaksi fasilitas tersebut.

        Parameter:
            list_reservasi: List Reservasi hasil filter fasilitas.
            total_pendapatan: Total pendapatan dari reservasi LUNAS dalam Decimal.
        """
        self._perbarui_kartu_pendapatan(total_pendapatan, len(list_reservasi))
        self._isi_tabel(list_reservasi)

    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan pesan kesalahan jika filter tidak valid atau data tidak ditemukan.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        QMessageBox.critical(self, "Gagal", pesan)

    # ------------------------------------------------------------------ #
    # Helper resolusi nama                                                 #
    # ------------------------------------------------------------------ #

    def _resolve_nama_warga(self, id_warga: str) -> str:
        if self._data_repository is None:
            return id_warga
        try:
            warga = self._data_repository.cari_warga(id_warga)
            return warga.nama if warga else id_warga
        except Exception:
            return id_warga

    def _resolve_nama_fasilitas(self, id_fasilitas: str) -> str:
        if self._data_repository is None:
            return id_fasilitas
        try:
            fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
            return fasilitas.nama if fasilitas else id_fasilitas
        except Exception:
            return id_fasilitas


# ------------------------------------------------------------------ #
# Kartu gradien untuk total pendapatan                                #
# ------------------------------------------------------------------ #

class _GradientCard(QFrame):
    """QFrame dengan latar gradien biru (primary → secondary)."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setMaximumHeight(130)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor("#003773"))
        grad.setColorAt(1.0, QColor("#4182fa"))

        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        painter.end()
