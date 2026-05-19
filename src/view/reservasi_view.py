from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QDateEdit,
    QSpinBox,
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
    """Helper form untuk proses reservasi: tambah dan ubah waktu (digunakan dari FasilitasView)."""

    def __init__(
        self,
        reservasi_controller: ReservasiController,
        data_repository: Optional[DataRepository] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._reservasi_ctrl = reservasi_controller
        self._data_repository = data_repository

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

        spin_jam_notif = QSpinBox()
        spin_jam_notif.setRange(1, 1440)
        spin_jam_notif.setValue(self._reservasi_ctrl.get_menit_notifikasi())
        spin_jam_notif.setSuffix(" menit sebelum berakhir")

        layout.addRow("ID Warga:", input_warga)
        layout.addRow("ID Fasilitas:", input_fasilitas)
        layout.addRow("Tanggal:", input_tanggal)
        layout.addRow("Jam Mulai:", input_jam_mulai)
        layout.addRow("Jam Selesai:", input_jam_selesai)
        layout.addRow("Notifikasi:", spin_jam_notif)

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
                spin_jam_notif.value(),
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Reservasi berhasil ditambahkan!")
                dialog.accept()
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
