from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from src.entity.enums import StatusReservasi
from src.entity.warga import Warga

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository


class WargaController:
    """Controller yang mengatur logika pengelolaan data warga (UC01-UC04)."""

    def __init__(self, data_repository: DataRepository) -> None:
        self._data_repository: DataRepository = data_repository

    def tambah_warga(self, nama: str, alamat: str, no_hp: str) -> bool:
        """Menambahkan data warga baru ke sistem setelah validasi data.

        Parameter:
            nama: Nama warga baru.
            alamat: Alamat warga baru.
            no_hp: Nomor HP warga baru.

        Returns:
            True jika warga berhasil ditambahkan, False jika validasi gagal.
        """
        if not self.validasi_data_warga(nama, alamat, no_hp):
            return False

        warga = Warga(str(uuid4()), nama, alamat, no_hp)
        return self._data_repository.tambah_warga(warga)

    def validasi_data_warga(self, nama: str, alamat: str, no_hp: str) -> bool:
        """Memvalidasi kelengkapan dan format data warga sebelum disimpan.

        Parameter:
            nama: Nama yang akan divalidasi (tidak boleh kosong).
            alamat: Alamat yang akan divalidasi (tidak boleh kosong).
            no_hp: Nomor HP yang akan divalidasi (hanya angka, tidak boleh kosong).

        Returns:
            True jika semua data valid, False jika ada data yang tidak memenuhi syarat.
        """
        return Warga("", nama, alamat, no_hp).validate_data()

    def lihat_daftar_warga(self) -> List[Warga]:
        """Mengambil seluruh data warga dari DataRepository.

        Returns:
            List berisi semua objek Warga yang tersimpan.
        """
        return self._data_repository.get_warga_list()

    def lihat_detail_warga(self, id_warga: str) -> Optional[Warga]:
        """Mengambil detail data warga berdasarkan ID.

        Parameter:
            id_warga: ID unik warga yang ingin dilihat.

        Returns:
            Objek Warga yang sesuai, atau None jika tidak ditemukan.
        """
        return self._data_repository.cari_warga(id_warga)

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
        warga = self._data_repository.cari_warga(id_warga)
        if warga is None or not self.validasi_data_warga(nama, alamat, no_hp):
            return False

        warga_baru = Warga(id_warga, nama, alamat, no_hp)
        return self._data_repository.ubah_warga(warga_baru)

    def hapus_warga(self, id_warga: str) -> bool:
        """Menghapus data warga dari sistem jika tidak memiliki reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika warga masih memiliki reservasi aktif.
        """
        warga = self._data_repository.cari_warga(id_warga)
        if warga is None or self.cek_reservasi_aktif_warga(id_warga):
            return False

        return self._data_repository.hapus_warga(warga)

    def cek_reservasi_aktif_warga(self, id_warga: str) -> bool:
        """Mengecek apakah warga masih memiliki reservasi dengan status BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga yang akan dicek.

        Returns:
            True jika warga masih punya reservasi aktif, False jika tidak ada.
        """
        return any(
            reservasi.id_warga == id_warga
            and reservasi.status == StatusReservasi.BELUM_DIBAYAR
            for reservasi in self._data_repository.get_list_reservasi()
        )
