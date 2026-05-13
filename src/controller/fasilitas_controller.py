from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from src.entity.enums import StatusFasilitas, StatusReservasi

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.fasilitas import Fasilitas


class FasilitasController:
    """Controller yang mengatur logika pengelolaan data fasilitas (UC05-UC08)."""

    def __init__(self, data_repository: DataRepository) -> None:
        self._data_repository: DataRepository = data_repository

    def validasi_data_fasilitas(
        self,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> bool:
        """Memvalidasi kelengkapan dan format data fasilitas sebelum disimpan."""
        if not nama or not str(nama).strip():
            return False
        try:
            if Decimal(str(harga_per_jam)) <= 0:
                return False
        except Exception:
            return False
        if not isinstance(status, StatusFasilitas):
            return False
        return True

    def tambah_fasilitas(
        self,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
        gambar: str = "",
    ) -> bool:
        """Menambahkan data fasilitas baru ke sistem setelah validasi data."""
        if not self.validasi_data_fasilitas(nama, harga_per_jam, deskripsi, status):
            return False
        from src.entity.fasilitas import Fasilitas
        id_baru = str(uuid.uuid4())
        fasilitas_baru = Fasilitas(
            id_baru, nama, Decimal(str(harga_per_jam)), deskripsi, status, gambar
        )
        return self._data_repository.tambah_fasilitas(fasilitas_baru)

    def lihat_daftar_fasilitas(self) -> List[Fasilitas]:
        """Mengambil seluruh data fasilitas dari DataRepository."""
        return self._data_repository.get_fasilitas_list()

    def lihat_detail_fasilitas(self, id_fasilitas: str) -> Optional[Fasilitas]:
        """Mengambil detail data fasilitas berdasarkan ID."""
        return self._data_repository.cari_fasilitas(id_fasilitas)

    def ubah_fasilitas(
        self,
        id_fasilitas: str,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
        gambar: str = "",
    ) -> bool:
        """Memperbarui data fasilitas yang sudah tersimpan berdasarkan ID."""
        if not self.validasi_data_fasilitas(nama, harga_per_jam, deskripsi, status):
            return False
        fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
        if fasilitas is None:
            return False
        fasilitas.ubah_data(nama, Decimal(str(harga_per_jam)), deskripsi, status, gambar)
        return self._data_repository.ubah_fasilitas(fasilitas)

    def cek_reservasi_aktif_fasilitas(self, id_fasilitas: str) -> bool:
        """Memeriksa apakah fasilitas masih terikat reservasi dengan status BELUM_DIBAYAR."""
        for r in self._data_repository.get_list_reservasi():
            if r.id_fasilitas == id_fasilitas and r.status == StatusReservasi.BELUM_DIBAYAR:
                return True
        return False

    def hapus_fasilitas(self, id_fasilitas: str) -> bool:
        """Menghapus data fasilitas dari sistem jika tidak ada reservasi BELUM_DIBAYAR."""
        if self.cek_reservasi_aktif_fasilitas(id_fasilitas):
            return False
        fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
        if fasilitas is None:
            return False
        return self._data_repository.hapus_fasilitas(fasilitas)