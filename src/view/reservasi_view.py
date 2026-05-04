from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget

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
        pass

    # TODO
    def tampilkan_total_biaya(self, total_biaya: Decimal) -> None:
        """Menampilkan estimasi total biaya yang dihitung secara otomatis berdasarkan
        durasi dan harga per jam fasilitas.

        Parameter:
            total_biaya: Total biaya dalam Decimal yang akan ditampilkan (format Rupiah).
        """
        pass

    # TODO
    def tampilkan_detail_reservasi(self, id_reservasi: str) -> None:
        """Menampilkan halaman detail reservasi beserta badge status pembayaran,
        tombol Tandai Lunas (jika BELUM_DIBAYAR), dan form ubah waktu (jika BELUM_DIBAYAR).

        Parameter:
            id_reservasi: ID reservasi yang ingin ditampilkan detailnya.
        """
        pass

    # TODO
    def tampilkan_form_ubah_waktu(self, id_reservasi: str) -> None:
        """Menampilkan form ubah waktu reservasi dengan nilai saat ini sebagai nilai awal.
        Hanya muncul jika status reservasi BELUM_DIBAYAR.

        Parameter:
            id_reservasi: ID reservasi yang waktunya akan diubah.
        """
        pass

    # TODO
    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses setelah operasi berhasil diproses.

        Parameter:
            pesan: Teks pesan sukses yang akan ditampilkan.
        """
        pass

    # TODO
    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error jika validasi atau operasi gagal.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        pass
