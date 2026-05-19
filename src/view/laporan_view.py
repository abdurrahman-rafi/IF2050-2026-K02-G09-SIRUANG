from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from src.entity.enums import StatusReservasi

if TYPE_CHECKING:
    from src.controller.laporan_controller import LaporanController
    from src.controller.reservasi_controller import ReservasiController
    from src.data.data_repository import DataRepository
    from src.entity.reservasi import Reservasi


class LaporanView(QWidget):
    """Tampilan laporan reservasi: daftar semua reservasi + detail inline + ringkasan pendapatan (UC12-UC13)."""

    def __init__(
        self,
        laporan_controller: LaporanController,
        data_repository: Optional[DataRepository] = None,
        reservasi_controller: Optional[ReservasiController] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._laporan_ctrl = laporan_controller
        self._data_repository = data_repository
        self._reservasi_ctrl = reservasi_controller

        self._combo_fasilitas: Optional[QComboBox] = None
        self._combo_status: Optional[QComboBox] = None
        self._input_dari: Optional[QDateEdit] = None
        self._input_sampai: Optional[QDateEdit] = None
        self._lbl_total: Optional[QLabel] = None
        self._lbl_jumlah: Optional[QLabel] = None
        self._tabel: Optional[QTableWidget] = None
        self._inner_stack: Optional[QStackedWidget] = None
        self._semua_reservasi: List[Reservasi] = []
        self._reservasi_tampil: List[Reservasi] = []

        self._setup_ui()
        self._muat_reservasi()

    # ------------------------------------------------------------------ #
    # Setup UI                                                             #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._inner_stack = QStackedWidget()
        self._inner_stack.addWidget(self._buat_halaman_daftar())
        outer.addWidget(self._inner_stack)

    def _buat_halaman_daftar(self) -> QWidget:
        page = QWidget()
        layout_outer = QVBoxLayout(page)
        layout_outer.setContentsMargins(0, 0, 0, 0)
        layout_outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        header = QLabel("Laporan Reservasi")
        header.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        layout.addWidget(header)

        layout.addWidget(self._buat_kartu_filter())
        layout.addWidget(self._buat_kartu_pendapatan())
        layout.addWidget(self._buat_tabel())

        scroll.setWidget(content)
        layout_outer.addWidget(scroll)
        return page

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

        self._combo_fasilitas = QComboBox()
        self._combo_fasilitas.setFixedHeight(34)
        self._combo_fasilitas.setMinimumWidth(180)
        self._combo_fasilitas.addItem("Semua Fasilitas", None)
        if self._data_repository is not None:
            try:
                for f in self._data_repository.get_fasilitas_list():
                    self._combo_fasilitas.addItem(f.nama, f.id_fasilitas)
            except Exception:
                pass
        baris.addWidget(self._combo_fasilitas)

        self._combo_status = QComboBox()
        self._combo_status.setFixedHeight(34)
        self._combo_status.setMinimumWidth(160)
        self._combo_status.addItem("Semua Status", None)
        self._combo_status.addItem("Belum Dibayar", StatusReservasi.BELUM_DIBAYAR)
        self._combo_status.addItem("Lunas", StatusReservasi.LUNAS)
        baris.addWidget(self._combo_status)

        lbl_dari = QLabel("Dari:")
        lbl_dari.setStyleSheet("color: #64748b; background: transparent;")
        lbl_dari.setFixedWidth(32)
        self._input_dari = QDateEdit(QDate.currentDate().addMonths(-1))
        self._input_dari.setCalendarPopup(True)
        self._input_dari.setFixedHeight(34)
        self._input_dari.setFixedWidth(130)
        baris.addWidget(lbl_dari)
        baris.addWidget(self._input_dari)

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

        self._lbl_jumlah = QLabel("dari 0 transaksi LUNAS")
        self._lbl_jumlah.setStyleSheet(
            "color: rgba(255,255,255,0.75); font-size: 12px; background: transparent;"
        )
        layout.addWidget(self._lbl_jumlah)

        return kartu

    def _buat_tabel(self) -> QTableWidget:
        self._tabel = QTableWidget()
        self._tabel.setColumnCount(7)
        self._tabel.setHorizontalHeaderLabels(
            ["Warga", "Fasilitas", "Tanggal", "Jam", "Total Biaya", "Status", "Aksi"]
        )
        self._tabel.verticalHeader().setVisible(False)
        self._tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabel.setAlternatingRowColors(True)
        self._tabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._tabel.verticalHeader().setDefaultSectionSize(40)

        hdr = self._tabel.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self._tabel.setColumnWidth(6, 90)

        self._tabel.cellDoubleClicked.connect(self._on_tabel_double_click)

        return self._tabel

    # ------------------------------------------------------------------ #
    # Halaman detail reservasi (inline)                                    #
    # ------------------------------------------------------------------ #

    def _buat_halaman_detail(self, reservasi: Reservasi) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(6)
        title_lbl = QLabel("Detail Reservasi")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a2e;")
        title_col.addWidget(title_lbl)

        if reservasi.status == StatusReservasi.LUNAS:
            badge_txt, badge_css = "LUNAS", (
                "color: #166534; background: #dcfce7; border-radius: 10px;"
                " padding: 3px 12px; font-size: 12px; font-weight: 700; border: none;"
            )
        else:
            badge_txt, badge_css = "BELUM DIBAYAR", (
                "color: #92400e; background: #fef3c7; border-radius: 10px;"
                " padding: 3px 12px; font-size: 12px; font-weight: 700; border: none;"
            )
        badge = QLabel(badge_txt)
        badge.setStyleSheet(badge_css)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        title_col.addWidget(badge)

        hdr_row.addLayout(title_col)
        hdr_row.addStretch()

        btn_kembali = QPushButton("← Kembali")
        btn_kembali.setProperty("outline", "true")
        btn_kembali.setFixedHeight(34)
        btn_kembali.clicked.connect(self._ke_daftar)
        hdr_row.addWidget(btn_kembali)
        layout.addLayout(hdr_row)

        # ---- Card 1: info grid ----
        info_card = self._buat_card()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(28, 22, 28, 22)
        info_layout.setSpacing(18)

        nama_warga = self._resolve_nama_warga(reservasi.id_warga)
        try:
            warga_obj = self._data_repository.cari_warga(reservasi.id_warga) if self._data_repository else None
            alamat_warga = warga_obj.alamat if warga_obj else "-"
            no_hp_warga = warga_obj.no_hp if warga_obj else "-"
        except Exception:
            alamat_warga, no_hp_warga = "-", "-"

        nama_fasilitas = self._resolve_nama_fasilitas(reservasi.id_fasilitas)
        try:
            fas_obj = self._data_repository.cari_fasilitas(reservasi.id_fasilitas) if self._data_repository else None
            harga_str = "Rp " + f"{int(fas_obj.harga_per_jam):,}".replace(",", ".") + "/jam" if fas_obj else "-"
        except Exception:
            harga_str = "-"

        tgl_str = reservasi.tanggal_dibuat.strftime("%d/%m/%Y") if reservasi.tanggal_dibuat else "-"
        jam_str = (
            f"{reservasi.jam_mulai.strftime('%H:%M')} – {reservasi.jam_selesai.strftime('%H:%M')}"
            if reservasi.jam_mulai and reservasi.jam_selesai else "-"
        )
        try:
            from datetime import datetime
            menit = (
                (reservasi.jam_selesai.hour * 60 + reservasi.jam_selesai.minute)
                - (reservasi.jam_mulai.hour * 60 + reservasi.jam_mulai.minute)
            )
            jam_durasi = menit // 60
            menit_sisa = menit % 60
            durasi_str = f"{jam_durasi} jam" + (f" {menit_sisa} menit" if menit_sisa else "")
        except Exception:
            durasi_str = "-"

        biaya_str = "Rp " + f"{int(reservasi.total_biaya):,}".replace(",", ".")

        fields = [
            ("NAMA WARGA", nama_warga),
            ("ALAMAT WARGA", alamat_warga),
            ("NO. HP", no_hp_warga),
            ("FASILITAS", nama_fasilitas),
            ("HARGA PER JAM", harga_str),
            ("TANGGAL", tgl_str),
            ("WAKTU", jam_str),
            ("DURASI", durasi_str),
            ("TOTAL BIAYA", biaya_str),
            ("STATUS PEMBAYARAN", badge_txt),
        ]

        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(14)

        for idx, (lbl_txt, val_txt) in enumerate(fields):
            col = idx % 2
            row = idx // 2
            grp = QVBoxLayout()
            grp.setSpacing(3)
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;"
                " background: transparent; border: none;"
            )
            val = QLabel(val_txt)
            val.setStyleSheet(
                "font-size: 14px; font-weight: 500; color: #1a1a2e;"
                " background: transparent; border: none;"
            )
            val.setWordWrap(True)
            grp.addWidget(lbl)
            grp.addWidget(val)
            w = QWidget()
            w.setLayout(grp)
            w.setStyleSheet("background: transparent;")
            grid.addWidget(w, row, col)

        info_layout.addLayout(grid)

        if reservasi.status == StatusReservasi.BELUM_DIBAYAR:
            btn_lunas = QPushButton("Tandai Lunas")
            btn_lunas.setFixedHeight(38)
            btn_lunas.setFixedWidth(160)

            def proses_lunas(checked=False, res=reservasi) -> None:
                berhasil = res.pembaruan_status_pembayaran()
                if berhasil:
                    if self._data_repository is not None:
                        try:
                            self._data_repository.ubah_reservasi(res)
                        except Exception:
                            pass
                    self.tampilkan_pesan_berhasil("Reservasi berhasil ditandai Lunas!")
                    self._ke_daftar()
                    self._muat_reservasi()

            btn_lunas.clicked.connect(proses_lunas)
            btn_row = QHBoxLayout()
            btn_row.addWidget(btn_lunas)
            btn_row.addStretch()
            info_layout.addLayout(btn_row)

        layout.addWidget(info_card)

        # ---- Card 2: ubah waktu (hanya jika BELUM_DIBAYAR) ----
        if reservasi.status == StatusReservasi.BELUM_DIBAYAR:
            ubah_card = self._buat_card()
            ubah_layout = QVBoxLayout(ubah_card)
            ubah_layout.setContentsMargins(28, 22, 28, 22)
            ubah_layout.setSpacing(14)

            ubah_title = QLabel("Ubah Waktu Reservasi")
            ubah_title.setStyleSheet(
                "font-size: 16px; font-weight: 700; color: #1a1a2e; background: transparent;"
            )
            ubah_layout.addWidget(ubah_title)

            from PyQt6.QtCore import QDate as _QDate, QTime as _QTime
            init_tgl = _QDate(
                reservasi.tanggal_dibuat.year,
                reservasi.tanggal_dibuat.month,
                reservasi.tanggal_dibuat.day,
            ) if reservasi.tanggal_dibuat else _QDate.currentDate()
            init_mulai = _QTime(reservasi.jam_mulai.hour, reservasi.jam_mulai.minute) \
                if reservasi.jam_mulai else _QTime(8, 0)
            init_selesai = _QTime(reservasi.jam_selesai.hour, reservasi.jam_selesai.minute) \
                if reservasi.jam_selesai else _QTime(10, 0)

            form = QFormLayout()
            form.setSpacing(12)

            input_tanggal = QDateEdit(init_tgl)
            input_tanggal.setCalendarPopup(True)
            input_jam_mulai = QTimeEdit(init_mulai)
            input_jam_selesai = QTimeEdit(init_selesai)

            form.addRow("Tanggal:", input_tanggal)
            form.addRow("Jam Mulai:", input_jam_mulai)
            form.addRow("Jam Selesai:", input_jam_selesai)
            ubah_layout.addLayout(form)

            btn_row2 = QHBoxLayout()
            btn_row2.addStretch()
            btn_simpan_ubah = QPushButton("Simpan Perubahan Waktu")
            btn_simpan_ubah.setProperty("outline", "true")
            btn_simpan_ubah.setFixedHeight(36)
            btn_row2.addWidget(btn_simpan_ubah)
            ubah_layout.addLayout(btn_row2)

            def proses_ubah(checked=False, res=reservasi) -> None:
                if self._reservasi_ctrl is None:
                    self.tampilkan_pesan_error("Fitur ubah waktu tidak tersedia.")
                    return
                berhasil = self._reservasi_ctrl.ubah_reservasi(
                    res.id_reservasi,
                    res.id_warga,
                    res.id_fasilitas,
                    input_tanggal.date().toPyDate(),
                    input_jam_mulai.time().toPyTime(),
                    input_jam_selesai.time().toPyTime(),
                )
                if berhasil:
                    self.tampilkan_pesan_berhasil("Jadwal reservasi berhasil diubah!")
                    self._ke_daftar()
                    self._muat_reservasi()
                else:
                    self.tampilkan_pesan_error(
                        "Gagal mengubah waktu.\n"
                        "Status mungkin sudah LUNAS atau jadwal baru bentrok."
                    )

            btn_simpan_ubah.clicked.connect(proses_ubah)
            layout.addWidget(ubah_card)

        layout.addStretch()
        scroll.setWidget(content)
        page_layout.addWidget(scroll)
        return page

    def _buat_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        return card

    # ------------------------------------------------------------------ #
    # Navigasi internal                                                    #
    # ------------------------------------------------------------------ #

    def _ke_daftar(self) -> None:
        if self._inner_stack is None:
            return
        if self._inner_stack.count() > 1:
            old = self._inner_stack.widget(1)
            self._inner_stack.removeWidget(old)
            old.deleteLater()
        self._inner_stack.setCurrentIndex(0)

    def _ke_detail(self, id_reservasi: str) -> None:
        semua = self._semua_reservasi
        reservasi = next((r for r in semua if r.id_reservasi == id_reservasi), None)
        if reservasi is None:
            self.tampilkan_pesan_error("Data reservasi tidak ditemukan.")
            return

        if self._inner_stack is None:
            return
        if self._inner_stack.count() > 1:
            old = self._inner_stack.widget(1)
            self._inner_stack.removeWidget(old)
            old.deleteLater()

        detail_page = self._buat_halaman_detail(reservasi)
        self._inner_stack.addWidget(detail_page)
        self._inner_stack.setCurrentIndex(1)

    def _on_tabel_double_click(self, row: int, col: int) -> None:
        if col == 6:
            return
        if row < len(self._reservasi_tampil):
            self._ke_detail(self._reservasi_tampil[row].id_reservasi)

    # ------------------------------------------------------------------ #
    # Data & filter                                                        #
    # ------------------------------------------------------------------ #

    def _muat_reservasi(self) -> None:
        try:
            if self._data_repository is not None:
                self._semua_reservasi = self._data_repository.get_list_reservasi()
            else:
                self._semua_reservasi = self._laporan_ctrl.lihat_riwayat_per_waktu(
                    date(2000, 1, 1), date.today()
                )
        except Exception:
            self._semua_reservasi = []
        self._terapkan_filter()

    def _terapkan_filter(self) -> None:
        id_fasilitas = self._combo_fasilitas.currentData() if self._combo_fasilitas else None
        filter_status: Optional[StatusReservasi] = (
            self._combo_status.currentData() if self._combo_status else None
        )
        dari = self._input_dari.date().toPyDate() if self._input_dari else date(2000, 1, 1)
        sampai = self._input_sampai.date().toPyDate() if self._input_sampai else date.today()

        hasil = self._semua_reservasi
        if id_fasilitas is not None:
            hasil = [r for r in hasil if r.id_fasilitas == id_fasilitas]
        if filter_status is not None:
            hasil = [r for r in hasil if r.status == filter_status]
        hasil = [
            r for r in hasil
            if r.tanggal_dibuat is None or dari <= r.tanggal_dibuat <= sampai
        ]

        lunas_list = [r for r in hasil if r.status == StatusReservasi.LUNAS]
        try:
            total = self._laporan_ctrl.hitung_total_pendapatan(lunas_list)
        except Exception:
            total = Decimal("0")

        self._perbarui_kartu_pendapatan(total, len(lunas_list))
        self._isi_tabel(hasil)

    def _perbarui_kartu_pendapatan(self, total: Decimal, jumlah_lunas: int) -> None:
        if self._lbl_total is not None:
            total_str = "Rp " + f"{int(total):,}".replace(",", ".")
            self._lbl_total.setText(total_str)
        if self._lbl_jumlah is not None:
            self._lbl_jumlah.setText(f"dari {jumlah_lunas} transaksi LUNAS")

    def _isi_tabel(self, daftar: List[Reservasi]) -> None:
        if self._tabel is None:
            return
        self._reservasi_tampil = list(daftar)
        self._tabel.setRowCount(0)

        if not daftar:
            self._tabel.setRowCount(1)
            item = QTableWidgetItem("Tidak ada data untuk filter yang dipilih.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(0, 0, item)
            self._tabel.setSpan(0, 0, 1, 7)
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

            # Tombol Lihat
            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(2, 2, 2, 2)
            aksi_layout.setSpacing(4)
            btn_lihat = QPushButton("Lihat")
            btn_lihat.setStyleSheet(
                "QPushButton { padding: 3px 10px; min-height: 22px; border-radius: 6px;"
                " background-color: #003773; color: white; font-weight: 600;"
                " font-size: 12px; border: none; }"
                "QPushButton:hover { background-color: #002555; }"
                "QPushButton:pressed { background-color: #001f40; }"
            )
            btn_lihat.clicked.connect(
                lambda checked=False, id_res=r.id_reservasi: self._ke_detail(id_res)
            )
            aksi_layout.addWidget(btn_lihat)
            self._tabel.setCellWidget(row, 6, aksi_widget)
            self._tabel.setRowHeight(row, 40)

    # ------------------------------------------------------------------ #
    # Metode publik                                                        #
    # ------------------------------------------------------------------ #

    def muat_ulang(self) -> None:
        """Kembali ke daftar dan muat ulang data reservasi."""
        self._ke_daftar()
        self._muat_reservasi()

    def tampilkan_laporan_per_waktu(
        self, list_reservasi: List[Reservasi], total_pendapatan: Decimal
    ) -> None:
        """Menampilkan laporan transaksi berdasarkan filter rentang waktu beserta
        card total pendapatan dan tabel 7-kolom riwayat transaksi.

        Parameter:
            list_reservasi: List Reservasi hasil filter rentang tanggal.
            total_pendapatan: Total pendapatan dari reservasi LUNAS dalam Decimal.
        """
        lunas_list = [r for r in list_reservasi if r.status == StatusReservasi.LUNAS]
        self._perbarui_kartu_pendapatan(total_pendapatan, len(lunas_list))
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
        lunas_list = [r for r in list_reservasi if r.status == StatusReservasi.LUNAS]
        self._perbarui_kartu_pendapatan(total_pendapatan, len(lunas_list))
        self._isi_tabel(list_reservasi)

    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog pesan sukses."""
        QMessageBox.information(self, "Berhasil", pesan)

    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan pesan kesalahan jika filter tidak valid atau data tidak ditemukan.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        QMessageBox.critical(self, "Gagal", pesan)

    # ------------------------------------------------------------------ #
    # Helper resolusi nama                                                 #
    # ------------------------------------------------------------------ #

    def _resolve_nama_warga(self, id_warga) -> str:
        if not id_warga:
            return "(Warga Dihapus)"
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
