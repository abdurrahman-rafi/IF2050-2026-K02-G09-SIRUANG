from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, List

from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from src.controller.laporan_controller import LaporanController
    from src.entity.reservasi import Reservasi


class LaporanView(QWidget):
    """Tampilan laporan riwayat transaksi dengan filter waktu dan fasilitas (UC12-UC13)."""

    def __init__(
        self,
        laporan_controller: LaporanController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._laporan_controller: LaporanController = laporan_controller

    # TODO
    def tampilkan_laporan_per_waktu(
        self, list_reservasi: List[Reservasi], total_pendapatan: Decimal
    ) -> None:
        """Menampilkan laporan transaksi berdasarkan filter rentang waktu beserta
        card total pendapatan dan tabel 6-kolom riwayat transaksi.

        Parameter:
            list_reservasi: List Reservasi hasil filter rentang tanggal.
            total_pendapatan: Total pendapatan dari reservasi LUNAS dalam Decimal.
        """
        pass

    # TODO
    def tampilkan_laporan_per_fasilitas(
        self, list_reservasi: List[Reservasi], total_pendapatan: Decimal
    ) -> None:
        """Menampilkan laporan transaksi berdasarkan filter fasilitas beserta
        card total pendapatan dan tabel riwayat transaksi fasilitas tersebut.

        Parameter:
            list_reservasi: List Reservasi hasil filter fasilitas.
            total_pendapatan: Total pendapatan dari reservasi LUNAS dalam Decimal.
        """
        pass

    # TODO
    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan pesan kesalahan jika filter tidak valid atau data tidak ditemukan.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        pass
