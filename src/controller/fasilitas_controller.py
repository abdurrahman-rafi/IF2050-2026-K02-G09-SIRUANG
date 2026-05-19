from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from src.entity.enums import StatusFasilitas, StatusReservasi
from src.entity.fasilitas_maintenance import FasilitasMaintenance

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
    ) -> Optional[str]:
        """Menambahkan data fasilitas baru ke sistem setelah validasi data.

        Returns:
            ID fasilitas baru jika berhasil, None jika gagal.
        """
        if not self.validasi_data_fasilitas(nama, harga_per_jam, deskripsi, status):
            return None
        from src.entity.fasilitas import Fasilitas
        id_baru = str(uuid.uuid4())
        fasilitas_baru = Fasilitas(
            id_baru, nama, Decimal(str(harga_per_jam)), deskripsi, status, gambar
        )
        berhasil = self._data_repository.tambah_fasilitas(fasilitas_baru)
        return id_baru if berhasil else None

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

    def set_maintenance(
        self,
        id_fasilitas: str,
        tanggal_mulai: date,
        tanggal_selesai: date,
        keterangan: str = "",
    ) -> bool:
        """Menyimpan atau memperbarui jadwal maintenance untuk fasilitas.
        Record maintenance lama dihapus terlebih dahulu sebelum menyimpan yang baru.

        Parameter:
            id_fasilitas: ID fasilitas yang akan dijadwalkan maintenance.
            tanggal_mulai: Tanggal mulai maintenance.
            tanggal_selesai: Tanggal selesai maintenance.
            keterangan: Catatan opsional tentang maintenance.

        Returns:
            True jika berhasil disimpan.
        """
        self._data_repository.hapus_maintenance_by_fasilitas(id_fasilitas)
        m = FasilitasMaintenance(
            str(uuid.uuid4()), id_fasilitas, tanggal_mulai, tanggal_selesai, keterangan
        )
        return self._data_repository.tambah_maintenance(m)

    def get_maintenance_aktif(self, id_fasilitas: str) -> Optional[FasilitasMaintenance]:
        """Mengambil record maintenance aktif untuk fasilitas (record pertama jika ada).

        Parameter:
            id_fasilitas: ID fasilitas yang dicari maintenance-nya.

        Returns:
            Objek FasilitasMaintenance jika ada, None jika tidak.
        """
        records = self._data_repository.get_maintenance_by_fasilitas(id_fasilitas)
        return records[0] if records else None

    def hapus_maintenance(self, id_fasilitas: str) -> bool:
        """Menghapus semua record maintenance untuk fasilitas (saat status diubah ke READY_TO_BOOK).

        Parameter:
            id_fasilitas: ID fasilitas yang maintenance-nya akan dihapus.

        Returns:
            True jika berhasil.
        """
        return self._data_repository.hapus_maintenance_by_fasilitas(id_fasilitas)