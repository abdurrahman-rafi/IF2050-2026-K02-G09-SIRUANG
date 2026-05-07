from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from datetime import date, time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, 
    QTimeEdit, QPushButton, QMessageBox, QLabel, QDialog
)
from PyQt6.QtCore import QDate, QTime

if TYPE_CHECKING:
    from src.controller.reservasi_controller import ReservasiController


class ReservasiView(QWidget):
    """Tampilan proses reservasi: form tambah, total biaya, detail, ubah waktu, dan status (UC09-UC11)."""

    def __init__(
        self,
        reservasi_controller: ReservasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._reservasi_controller: ReservasiController = reservasi_controller

    # TODO
    def tampilkan_form_tambah_reservasi(self) -> None:
        """Menampilkan form penambahan reservasi baru (pilih warga, tanggal, jam mulai, jam selesai)
        dan memanggil tambah_reservasi() pada ReservasiController saat disimpan."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Reservasi Baru")
        layout = QFormLayout(dialog)

        input_warga = QLineEdit()
        input_fasilitas = QLineEdit()
        
        input_tanggal = QDateEdit()
        input_tanggal.setDate(QDate.currentDate())
        input_tanggal.setCalendarPopup(True)
        
        input_jam_mulai = QTimeEdit()
        input_jam_selesai = QTimeEdit()

        layout.addRow("ID Warga:", input_warga)
        layout.addRow("ID Fasilitas:", input_fasilitas)
        layout.addRow("Tanggal:", input_tanggal)
        layout.addRow("Jam Mulai:", input_jam_mulai)
        layout.addRow("Jam Selesai:", input_jam_selesai)

        btn_simpan = QPushButton("Simpan Reservasi")
        layout.addRow(btn_simpan)

        def proses_simpan():
            warga_val = input_warga.text()
            fasilitas_val = input_fasilitas.text()
            tgl_val = input_tanggal.date().toPyDate()
            mulai_val = input_jam_mulai.time().toPyTime()
            selesai_val = input_jam_selesai.time().toPyTime()

            berhasil = self._reservasi_controller.tambah_reservasi(
                warga_val, fasilitas_val, tgl_val, mulai_val, selesai_val
            )

            if berhasil:
                self.tampilkan_pesan_berhasil("Reservasi berhasil ditambahkan!")
                dialog.accept()
            else:
                self.tampilkan_pesan_error("Gagal menambahkan reservasi. Jadwal mungkin bentrok.")

        btn_simpan.clicked.connect(proses_simpan)
        dialog.exec()

    
    # TODO
    def tampilkan_total_biaya(self, total_biaya: Decimal) -> None:
        """Menampilkan estimasi total biaya yang dihitung secara otomatis berdasarkan
        durasi dan harga per jam fasilitas.

        Parameter:
            total_biaya: Total biaya dalam Decimal yang akan ditampilkan (format Rupiah).
        """
        self.tampilkan_pesan_berhasil(f"Estimasi Total Biaya Reservasi:\nRp {total_biaya:,.2f}")
        pass

    # TODO
    def tampilkan_detail_reservasi(self, id_reservasi: str) -> None:
        """Menampilkan halaman detail reservasi beserta badge status pembayaran,
        tombol Tandai Lunas (jika BELUM_DIBAYAR), dan form ubah waktu (jika BELUM_DIBAYAR).

        Parameter:
            id_reservasi: ID reservasi yang ingin ditampilkan detailnya.
        """
        QMessageBox.information(self, "Detail Reservasi", f"Menampilkan detail data untuk ID:\n{id_reservasi}")
        pass

    # TODO
    def tampilkan_form_ubah_waktu(self, id_reservasi: str) -> None:
        """Menampilkan form ubah waktu reservasi dengan nilai saat ini sebagai nilai awal.
        Hanya muncul jika status reservasi BELUM_DIBAYAR.

        Parameter:
            id_reservasi: ID reservasi yang waktunya akan diubah.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ubah Waktu Reservasi - {id_reservasi}")
        layout = QFormLayout(dialog)

        input_warga = QLineEdit()
        input_fasilitas = QLineEdit()
        
        input_tanggal = QDateEdit(QDate.currentDate())
        input_tanggal.setCalendarPopup(True)
        
        input_jam_mulai = QTimeEdit()
        input_jam_selesai = QTimeEdit()

        layout.addRow("ID Warga (Baru):", input_warga)
        layout.addRow("ID Fasilitas (Baru):", input_fasilitas)
        layout.addRow("Tanggal Baru:", input_tanggal)
        layout.addRow("Jam Mulai Baru:", input_jam_mulai)
        layout.addRow("Jam Selesai Baru:", input_jam_selesai)

        btn_ubah = QPushButton("Simpan Perubahan")
        layout.addRow(btn_ubah)

        # Sama seperti form tambah, ini hanya fungsi internal untuk tombol
        def proses_ubah():
            warga_val = input_warga.text()
            fasilitas_val = input_fasilitas.text()
            tgl_val = input_tanggal.date().toPyDate()
            mulai_val = input_jam_mulai.time().toPyTime()
            selesai_val = input_jam_selesai.time().toPyTime()

            berhasil = self._reservasi_controller.ubah_reservasi(
                id_reservasi, warga_val, fasilitas_val, tgl_val, mulai_val, selesai_val
            )

            if berhasil:
                self.tampilkan_pesan_berhasil("Jadwal reservasi berhasil diubah!")
                dialog.accept()
            else:
                self.tampilkan_pesan_error("Gagal mengubah waktu.\nStatus mungkin sudah LUNAS atau jadwal baru bentrok.")

        btn_ubah.clicked.connect(proses_ubah)
        dialog.exec()
        pass

    # TODO
    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses setelah operasi berhasil diproses.

        Parameter:
            pesan: Teks pesan sukses yang akan ditampilkan.
        """
        QMessageBox.information(self, "Sukses", pesan)
        

    # TODO
    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error jika validasi atau operasi gagal.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        QMessageBox.critical(self, "Gagal", pesan)
        