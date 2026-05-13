from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QDateEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from src.entity.enums import StatusReservasi

if TYPE_CHECKING:
    from src.controller.reservasi_controller import ReservasiController
    from src.data.data_repository import DataRepository
    from src.entity.reservasi import Reservasi


class ReservasiView(QWidget):
    """Tampilan proses reservasi: daftar, tambah, detail, ubah waktu, dan status (UC09-UC11)."""

    def __init__(
        self,
        reservasi_controller: ReservasiController,
        data_repository: Optional[DataRepository] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._reservasi_ctrl = reservasi_controller
        self._data_repository = data_repository
        self._semua_reservasi: List[Reservasi] = []
        self._tabel: Optional[QTableWidget] = None
        self._input_cari: Optional[QLineEdit] = None
        self._combo_status: Optional[QComboBox] = None
        self._setup_ui()
        self._muat_reservasi()

    # ------------------------------------------------------------------ #
    # Setup halaman daftar                                                 #
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
        layout.setSpacing(16)

        # Header: judul + tombol tambah
        header = QHBoxLayout()
        judul = QLabel("Reservasi")
        judul.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a2e; background: transparent;")
        header.addWidget(judul)
        header.addStretch()
        btn_tambah = QPushButton("+ Tambah Reservasi")
        btn_tambah.setFixedHeight(36)
        btn_tambah.clicked.connect(self.tampilkan_form_tambah_reservasi)
        header.addWidget(btn_tambah)
        layout.addLayout(header)

        # Filter: cari + status
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self._input_cari = QLineEdit()
        self._input_cari.setPlaceholderText("Cari ID warga atau fasilitas...")
        self._input_cari.setFixedHeight(34)
        self._input_cari.textChanged.connect(self._terapkan_filter)
        filter_row.addWidget(self._input_cari)

        self._combo_status = QComboBox()
        self._combo_status.setFixedHeight(34)
        self._combo_status.setMinimumWidth(160)
        self._combo_status.addItem("Semua Status", None)
        self._combo_status.addItem("Belum Dibayar", StatusReservasi.BELUM_DIBAYAR)
        self._combo_status.addItem("Lunas", StatusReservasi.LUNAS)
        self._combo_status.currentIndexChanged.connect(self._terapkan_filter)
        filter_row.addWidget(self._combo_status)
        layout.addLayout(filter_row)

        # Tabel
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

        hdr = self._tabel.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self._tabel.setColumnWidth(6, 120)

        layout.addWidget(self._tabel)

        scroll.setWidget(page)
        outer.addWidget(scroll)

    def _muat_reservasi(self) -> None:
        try:
            self._semua_reservasi = self._reservasi_ctrl.lihat_daftar_reservasi()
        except Exception:
            self._semua_reservasi = []
        self._terapkan_filter()

    def _terapkan_filter(self) -> None:
        if self._tabel is None:
            return
        kata = (self._input_cari.text().strip().lower()) if self._input_cari else ""
        filter_status: Optional[StatusReservasi] = (
            self._combo_status.currentData() if self._combo_status else None
        )

        hasil = [
            r for r in self._semua_reservasi
            if (kata in r.id_warga.lower() or kata in r.id_fasilitas.lower())
            and (filter_status is None or r.status == filter_status)
        ]
        self._isi_tabel(hasil)

    def _isi_tabel(self, daftar: List[Reservasi]) -> None:
        if self._tabel is None:
            return
        self._tabel.setRowCount(0)

        if not daftar:
            self._tabel.setRowCount(1)
            item = QTableWidgetItem("Tidak ada data reservasi.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(0, 0, item)
            self._tabel.setSpan(0, 0, 1, 7)
            return

        self._tabel.setSpan(0, 0, 1, 1)  # reset span jika ada
        self._tabel.setRowCount(len(daftar))

        for row, r in enumerate(daftar):
            nama_warga = self._resolve_nama_warga(r.id_warga)
            nama_fasilitas = self._resolve_nama_fasilitas(r.id_fasilitas)
            tanggal_str = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
            jam_str = (
                f"{r.jam_mulai.strftime('%H:%M')} - {r.jam_selesai.strftime('%H:%M')}"
                if r.jam_mulai and r.jam_selesai else "-"
            )
            biaya_str = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")

            self._tabel.setItem(row, 0, QTableWidgetItem(nama_warga))
            self._tabel.setItem(row, 1, QTableWidgetItem(nama_fasilitas))
            self._tabel.setItem(row, 2, QTableWidgetItem(tanggal_str))
            self._tabel.setItem(row, 3, QTableWidgetItem(jam_str))
            self._tabel.setItem(row, 4, QTableWidgetItem(biaya_str))

            # Status badge
            if r.status == StatusReservasi.LUNAS:
                status_item = QTableWidgetItem("LUNAS")
                status_item.setForeground(QColor("#166534"))
                status_item.setBackground(QColor("#dcfce7"))
            else:
                status_item = QTableWidgetItem("BELUM DIBAYAR")
                status_item.setForeground(QColor("#92400e"))
                status_item.setBackground(QColor("#fef3c7"))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(row, 5, status_item)

            # Tombol aksi
            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(4, 2, 4, 2)
            btn_lihat = QPushButton("Lihat")
            btn_lihat.setFixedHeight(28)
            btn_lihat.clicked.connect(
                lambda checked=False, id_res=r.id_reservasi: self.tampilkan_detail_reservasi(id_res)
            )
            aksi_layout.addWidget(btn_lihat)
            self._tabel.setCellWidget(row, 6, aksi_widget)

    # ------------------------------------------------------------------ #
    # Metode publik                                                        #
    # ------------------------------------------------------------------ #

    def muat_ulang(self) -> None:
        """Memuat ulang data reservasi dari controller."""
        self._muat_reservasi()

    def tampilkan_form_tambah_reservasi(self) -> None:
        """Menampilkan form penambahan reservasi baru (pilih warga, tanggal, jam mulai, jam selesai)
        dan memanggil tambah_reservasi() pada ReservasiController saat disimpan."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Reservasi Baru")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        layout.setSpacing(12)

        input_warga = QLineEdit()
        input_warga.setPlaceholderText("ID Warga")
        input_fasilitas = QLineEdit()
        input_fasilitas.setPlaceholderText("ID Fasilitas")

        input_tanggal = QDateEdit(QDate.currentDate())
        input_tanggal.setCalendarPopup(True)

        input_jam_mulai = QTimeEdit()
        input_jam_selesai = QTimeEdit()

        layout.addRow("ID Warga:", input_warga)
        layout.addRow("ID Fasilitas:", input_fasilitas)
        layout.addRow("Tanggal:", input_tanggal)
        layout.addRow("Jam Mulai:", input_jam_mulai)
        layout.addRow("Jam Selesai:", input_jam_selesai)

        baris_tombol = QHBoxLayout()
        btn_batal = QPushButton("Batal")
        btn_batal.setProperty("outline", "true")
        btn_batal.clicked.connect(dialog.reject)
        btn_simpan = QPushButton("Simpan Reservasi")
        baris_tombol.addWidget(btn_batal)
        baris_tombol.addStretch()
        baris_tombol.addWidget(btn_simpan)
        layout.addRow(baris_tombol)

        def proses_simpan() -> None:
            berhasil = self._reservasi_ctrl.tambah_reservasi(
                input_warga.text().strip(),
                input_fasilitas.text().strip(),
                input_tanggal.date().toPyDate(),
                input_jam_mulai.time().toPyTime(),
                input_jam_selesai.time().toPyTime(),
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Reservasi berhasil ditambahkan!")
                dialog.accept()
                self._muat_reservasi()
            else:
                self.tampilkan_pesan_error(
                    "Gagal menambahkan reservasi.\nPastikan jadwal tidak bentrok dan data valid."
                )

        btn_simpan.clicked.connect(proses_simpan)
        dialog.exec()

    def tampilkan_total_biaya(self, total_biaya: Decimal) -> None:
        """Menampilkan estimasi total biaya yang dihitung secara otomatis berdasarkan
        durasi dan harga per jam fasilitas.

        Parameter:
            total_biaya: Total biaya dalam Decimal yang akan ditampilkan (format Rupiah).
        """
        biaya_str = "Rp " + f"{int(total_biaya):,}".replace(",", ".")
        self.tampilkan_pesan_berhasil(f"Estimasi Total Biaya Reservasi:\n{biaya_str}")

    def tampilkan_detail_reservasi(self, id_reservasi: str) -> None:
        """Menampilkan halaman detail reservasi beserta badge status pembayaran,
        tombol Tandai Lunas (jika BELUM_DIBAYAR), dan form ubah waktu (jika BELUM_DIBAYAR).

        Parameter:
            id_reservasi: ID reservasi yang ingin ditampilkan detailnya.
        """
        try:
            semua = self._reservasi_ctrl.lihat_daftar_reservasi()
        except Exception:
            semua = []
        reservasi = next((r for r in semua if r.id_reservasi == id_reservasi), None)

        if reservasi is None:
            self.tampilkan_pesan_error("Data reservasi tidak ditemukan.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detail Reservasi — {id_reservasi}")
        dialog.setMinimumWidth(460)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(8)

        nama_warga = self._resolve_nama_warga(reservasi.id_warga)
        nama_fasilitas = self._resolve_nama_fasilitas(reservasi.id_fasilitas)

        form.addRow("ID Reservasi:", QLabel(reservasi.id_reservasi))
        form.addRow("Warga:",        QLabel(f"{nama_warga} ({reservasi.id_warga})"))
        form.addRow("Fasilitas:",    QLabel(f"{nama_fasilitas} ({reservasi.id_fasilitas})"))
        form.addRow("Tanggal:",      QLabel(reservasi.tanggal_dibuat.strftime("%d %B %Y")))
        jam_str = (
            f"{reservasi.jam_mulai.strftime('%H:%M')} – {reservasi.jam_selesai.strftime('%H:%M')}"
        )
        form.addRow("Jam:",          QLabel(jam_str))
        biaya_str = "Rp " + f"{int(reservasi.total_biaya):,}".replace(",", ".")
        form.addRow("Total Biaya:",  QLabel(biaya_str))

        if reservasi.status == StatusReservasi.LUNAS:
            badge = QLabel("LUNAS")
            badge.setStyleSheet(
                "color: #166534; background: #dcfce7; border-radius: 6px;"
                " padding: 3px 10px; font-weight: 700;"
            )
        else:
            badge = QLabel("BELUM DIBAYAR")
            badge.setStyleSheet(
                "color: #92400e; background: #fef3c7; border-radius: 6px;"
                " padding: 3px 10px; font-weight: 700;"
            )
        form.addRow("Status:", badge)
        layout.addLayout(form)

        if reservasi.status == StatusReservasi.BELUM_DIBAYAR:
            btn_row = QHBoxLayout()

            btn_lunas = QPushButton("Tandai Lunas")

            btn_ubah = QPushButton("Ubah Waktu")
            btn_ubah.setProperty("outline", "true")

            btn_tutup = QPushButton("Tutup")
            btn_tutup.setProperty("outline", "true")
            btn_tutup.clicked.connect(dialog.reject)

            def proses_lunas() -> None:
                berhasil = reservasi.pembaruan_status_pembayaran()
                if berhasil:
                    repo = self._data_repository or getattr(
                        self._reservasi_ctrl, "_data_repository", None
                    )
                    if repo is not None:
                        try:
                            repo.ubah_reservasi(reservasi)
                        except Exception:
                            pass
                    self.tampilkan_pesan_berhasil("Reservasi berhasil ditandai Lunas!")
                    dialog.accept()
                    self._muat_reservasi()

            def proses_ubah_waktu() -> None:
                dialog.accept()
                self.tampilkan_form_ubah_waktu(id_reservasi)

            btn_lunas.clicked.connect(proses_lunas)
            btn_ubah.clicked.connect(proses_ubah_waktu)

            btn_row.addWidget(btn_lunas)
            btn_row.addWidget(btn_ubah)
            btn_row.addStretch()
            btn_row.addWidget(btn_tutup)
            layout.addLayout(btn_row)
        else:
            btn_tutup = QPushButton("Tutup")
            btn_tutup.setProperty("outline", "true")
            btn_tutup.clicked.connect(dialog.reject)
            layout.addWidget(btn_tutup, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()

    def tampilkan_form_ubah_waktu(self, id_reservasi: str) -> None:
        """Menampilkan form ubah waktu reservasi dengan nilai saat ini sebagai nilai awal.
        Hanya muncul jika status reservasi BELUM_DIBAYAR.

        Parameter:
            id_reservasi: ID reservasi yang waktunya akan diubah.
        """
        try:
            semua = self._reservasi_ctrl.lihat_daftar_reservasi()
        except Exception:
            semua = []
        reservasi = next((r for r in semua if r.id_reservasi == id_reservasi), None)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ubah Waktu Reservasi — {id_reservasi}")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        layout.setSpacing(12)

        if reservasi is not None:
            init_tanggal = QDate(
                reservasi.tanggal_dibuat.year,
                reservasi.tanggal_dibuat.month,
                reservasi.tanggal_dibuat.day,
            )
            init_mulai = QTime(reservasi.jam_mulai.hour, reservasi.jam_mulai.minute)
            init_selesai = QTime(reservasi.jam_selesai.hour, reservasi.jam_selesai.minute)
        else:
            init_tanggal = QDate.currentDate()
            init_mulai = QTime(8, 0)
            init_selesai = QTime(10, 0)

        input_tanggal = QDateEdit(init_tanggal)
        input_tanggal.setCalendarPopup(True)
        input_jam_mulai = QTimeEdit(init_mulai)
        input_jam_selesai = QTimeEdit(init_selesai)

        layout.addRow("Tanggal Baru:", input_tanggal)
        layout.addRow("Jam Mulai Baru:", input_jam_mulai)
        layout.addRow("Jam Selesai Baru:", input_jam_selesai)

        baris_tombol = QHBoxLayout()
        btn_batal = QPushButton("Batal")
        btn_batal.setProperty("outline", "true")
        btn_batal.clicked.connect(dialog.reject)
        btn_simpan = QPushButton("Simpan Perubahan")
        baris_tombol.addWidget(btn_batal)
        baris_tombol.addStretch()
        baris_tombol.addWidget(btn_simpan)
        layout.addRow(baris_tombol)

        def proses_ubah() -> None:
            id_warga_val = reservasi.id_warga if reservasi else ""
            id_fasilitas_val = reservasi.id_fasilitas if reservasi else ""
            berhasil = self._reservasi_ctrl.ubah_reservasi(
                id_reservasi,
                id_warga_val,
                id_fasilitas_val,
                input_tanggal.date().toPyDate(),
                input_jam_mulai.time().toPyTime(),
                input_jam_selesai.time().toPyTime(),
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Jadwal reservasi berhasil diubah!")
                dialog.accept()
                self._muat_reservasi()
            else:
                self.tampilkan_pesan_error(
                    "Gagal mengubah waktu.\n"
                    "Status mungkin sudah LUNAS atau jadwal baru bentrok."
                )

        btn_simpan.clicked.connect(proses_ubah)
        dialog.exec()

    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses setelah operasi berhasil diproses.

        Parameter:
            pesan: Teks pesan sukses yang akan ditampilkan.
        """
        QMessageBox.information(self, "Berhasil", pesan)

    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error jika validasi atau operasi gagal.

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
