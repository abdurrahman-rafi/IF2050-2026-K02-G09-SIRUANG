from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List

from src.entity.enums import StatusReservasi

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.reservasi import Reservasi


class LaporanController:
    """Controller yang mengatur logika pengambilan dan pemfilteran data laporan (UC12-UC13)."""

    def __init__(self, data_repository: DataRepository) -> None:
        self._data_repository: DataRepository = data_repository

    def lihat_riwayat_per_waktu(
        self, tanggal_mulai: date, tanggal_selesai: date
    ) -> List[Reservasi]:
        """Mengambil daftar reservasi dalam rentang tanggal yang dipilih.

        Parameter:
            tanggal_mulai: Tanggal awal filter laporan.
            tanggal_selesai: Tanggal akhir filter laporan (harus >= tanggal_mulai).

        Returns:
            List Reservasi dalam rentang tanggal tersebut, atau list kosong jika tidak ada.
        """
        if tanggal_selesai < tanggal_mulai:
            return []
        return self._data_repository.cari_reservasi_by_date_range(
            tanggal_mulai, tanggal_selesai
        )

    def lihat_riwayat_per_fasilitas(self, id_fasilitas: str) -> List[Reservasi]:
        """Mengambil seluruh riwayat reservasi berdasarkan fasilitas tertentu.

        Parameter:
            id_fasilitas: ID fasilitas yang riwayat transaksinya ingin dilihat.

        Returns:
            List semua Reservasi untuk fasilitas tersebut, atau list kosong jika tidak ada.
        """
        return self._data_repository.cari_reservasi_by_fasilitas(id_fasilitas)

    def hitung_total_pendapatan(self, list_reservasi: List[Reservasi]) -> Decimal:
        """Menghitung total pendapatan dari daftar reservasi yang diberikan.
        Hanya menjumlahkan reservasi dengan status LUNAS.

        Parameter:
            list_reservasi: List Reservasi yang akan dihitung total pendapatannya.

        Returns:
            Total pendapatan dalam Decimal (Rupiah), atau Decimal('0') jika tidak ada.
        """
        return sum(
            (r.total_biaya for r in list_reservasi if r.status == StatusReservasi.LUNAS),
            Decimal("0"),
        )
