from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.warga import Warga


class WargaController:
    """Controller yang mengatur logika pengelolaan data warga (UC01-UC04)."""

    def __init__(self, data_repository: DataRepository) -> None:
        self._data_repository: DataRepository = data_repository

    # TODO
    def tambah_warga(self, nama: str, alamat: str, no_hp: str) -> bool:
        """Menambahkan data warga baru ke sistem setelah validasi data.

        Parameter:
            nama: Nama warga baru.
            alamat: Alamat warga baru.
            no_hp: Nomor HP warga baru.

        Returns:
            True jika warga berhasil ditambahkan, False jika validasi gagal.
        """
        pass

    # TODO
    def validasi_data_warga(self, nama: str, alamat: str, no_hp: str) -> bool:
        """Memvalidasi kelengkapan dan format data warga sebelum disimpan.

        Parameter:
            nama: Nama yang akan divalidasi (tidak boleh kosong).
            alamat: Alamat yang akan divalidasi (tidak boleh kosong).
            no_hp: Nomor HP yang akan divalidasi (hanya angka, tidak boleh kosong).

        Returns:
            True jika semua data valid, False jika ada data yang tidak memenuhi syarat.
        """
        pass

    # TODO
    def lihat_daftar_warga(self) -> List[Warga]:
        """Mengambil seluruh data warga dari DataRepository.

        Returns:
            List berisi semua objek Warga yang tersimpan.
        """
        pass

    # TODO
    def lihat_detail_warga(self, id_warga: str) -> Optional[Warga]:
        """Mengambil detail data warga berdasarkan ID.

        Parameter:
            id_warga: ID unik warga yang ingin dilihat.

        Returns:
            Objek Warga yang sesuai, atau None jika tidak ditemukan.
        """
        pass

    # TODO
    def ubah_warga(self, id_warga: str, nama: str, alamat: str, no_hp: str) -> bool:
        """Memperbarui data warga yang sudah tersimpan berdasarkan ID.

        Parameter:
            id_warga: ID warga yang datanya akan diperbarui.
            nama: Nama baru.
            alamat: Alamat baru.
            no_hp: Nomor HP baru.

        Returns:
            True jika pembaruan berhasil, False jika data tidak valid atau warga tidak ditemukan.
        """
        pass

    # TODO
    def hapus_warga(self, id_warga: str) -> bool:
        """Menghapus data warga dari sistem jika tidak memiliki reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika warga masih memiliki reservasi aktif.
        """
        pass

    # TODO
    def cek_reservasi_aktif_warga(self, id_warga: str) -> bool:
        """Mengecek apakah warga masih memiliki reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga yang akan dicek.

        Returns:
            True jika warga masih punya reservasi aktif, False jika tidak ada.
        """
        pass
