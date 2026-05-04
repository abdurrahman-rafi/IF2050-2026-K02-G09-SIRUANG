from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from src.entity.enums import StatusFasilitas

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.fasilitas import Fasilitas


class FasilitasController:
    """Controller yang mengatur logika pengelolaan data fasilitas (UC05-UC08)."""

    def __init__(self, data_repository: DataRepository) -> None:
        self._data_repository: DataRepository = data_repository

    # TODO
    def tambah_fasilitas(
        self,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> bool:
        """Menambahkan data fasilitas baru ke sistem setelah validasi data.

        Parameter:
            nama: Nama fasilitas baru.
            harga_per_jam: Harga sewa per jam dalam Decimal (Rupiah).
            deskripsi: Deskripsi fasilitas.
            status: Status awal fasilitas (READY_TO_BOOK atau MAINTENANCE).

        Returns:
            True jika fasilitas berhasil ditambahkan, False jika validasi gagal.
        """
        pass

    # TODO
    def validasi_data_fasilitas(
        self,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> bool:
        """Memvalidasi kelengkapan dan format data fasilitas sebelum disimpan.

        Parameter:
            nama: Nama fasilitas (tidak boleh kosong).
            harga_per_jam: Harga per jam (harus lebih dari 0).
            deskripsi: Deskripsi fasilitas.
            status: Status fasilitas (harus nilai StatusFasilitas yang valid).

        Returns:
            True jika semua data valid, False jika ada data yang tidak memenuhi syarat.
        """
        pass

    # TODO
    def lihat_daftar_fasilitas(self) -> List[Fasilitas]:
        """Mengambil seluruh data fasilitas dari DataRepository.

        Returns:
            List berisi semua objek Fasilitas yang tersimpan.
        """
        pass

    # TODO
    def lihat_detail_fasilitas(self, id_fasilitas: str) -> Optional[Fasilitas]:
        """Mengambil detail data fasilitas berdasarkan ID.

        Parameter:
            id_fasilitas: ID unik fasilitas yang ingin dilihat.

        Returns:
            Objek Fasilitas yang sesuai, atau None jika tidak ditemukan.
        """
        pass

    # TODO
    def ubah_fasilitas(
        self,
        id_fasilitas: str,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> bool:
        """Memperbarui data fasilitas yang sudah tersimpan berdasarkan ID.

        Parameter:
            id_fasilitas: ID fasilitas yang datanya akan diperbarui.
            nama: Nama baru.
            harga_per_jam: Harga per jam baru (Decimal).
            deskripsi: Deskripsi baru.
            status: Status baru fasilitas.

        Returns:
            True jika pembaruan berhasil, False jika data tidak valid atau fasilitas tidak ditemukan.
        """
        pass

    # TODO
    def hapus_fasilitas(self, id_fasilitas: str) -> bool:
        """Menghapus data fasilitas dari sistem jika tidak ada reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_fasilitas: ID fasilitas yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika fasilitas masih punya reservasi aktif.
        """
        pass

    # TODO
    def cek_reservasi_aktif_fasilitas(self, id_fasilitas: str) -> bool:
        """Memeriksa apakah fasilitas masih terikat reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_fasilitas: ID fasilitas yang akan dicek.

        Returns:
            True jika ada reservasi aktif, False jika tidak ada.
        """
        pass
