from __future__ import annotations
from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from src.entity.enums import StatusFasilitas, StatusReservasi
from src.entity.fasilitas import Fasilitas
from src.entity.notifikasi import Notifikasi
from src.entity.reservasi import Reservasi
from src.entity.warga import Warga

if TYPE_CHECKING:
    from src.data.database_manager import DatabaseManager


class DataRepository:
    """Lapisan penyimpanan sementara (in-memory list) dan antarmuka ke DatabaseManager
    untuk seluruh entitas sistem."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager: DatabaseManager = database_manager
        self._list_warga: List[Warga] = []
        self._list_fasilitas: List[Fasilitas] = []
        self._list_reservasi: List[Reservasi] = []
        self._list_notifikasi: List[Notifikasi] = []
        self._muat_data()

    def _muat_data(self) -> None:
        """Memuat seluruh data dari database ke list in-memory saat inisialisasi."""
        for row in self._database_manager.ambil_data("SELECT * FROM warga", ()):
            self._list_warga.append(
                Warga(row["id_warga"], row["nama"], row["alamat"], row["no_hp"])
            )

        for row in self._database_manager.ambil_data("SELECT * FROM fasilitas", ()):
            self._list_fasilitas.append(
                Fasilitas(
                    row["id_fasilitas"],
                    row["nama"],
                    Decimal(str(row["harga_per_jam"])),
                    row["deskripsi"] or "",
                    StatusFasilitas(row["status"]),
                )
            )

        for row in self._database_manager.ambil_data("SELECT * FROM reservasi", ()):
            self._list_reservasi.append(
                Reservasi(
                    row["id_reservasi"],
                    row["id_warga"],
                    row["id_fasilitas"],
                    row["tanggal_dibuat"],
                    row["jam_mulai"] if isinstance(row["jam_mulai"], time) else time.fromisoformat(str(row["jam_mulai"])),
                    row["jam_selesai"] if isinstance(row["jam_selesai"], time) else time.fromisoformat(str(row["jam_selesai"])),
                    Decimal(str(row["total_biaya"])),
                    StatusReservasi(row["status"]),
                )
            )

        for row in self._database_manager.ambil_data("SELECT * FROM notifikasi", ()):
            self._list_notifikasi.append(
                Notifikasi(
                    row["id_notifikasi"],
                    row["id_reservasi"],
                    row["pesan_notifikasi"],
                    row["waktu_kirim"],
                    bool(row["sudah_dibaca"]),
                )
            )

    # Warga

    def tambah_warga(self, w: Warga) -> bool:
        """Menyimpan objek warga baru ke list in-memory dan ke database.

        Parameter:
            w: Objek Warga yang akan disimpan.

        Returns:
            True jika penyimpanan berhasil, False jika gagal.
        """
        query = "INSERT INTO warga (id_warga, nama, alamat, no_hp) VALUES (%s, %s, %s, %s)"
        berhasil = self._database_manager.simpan_data(
            query, (w.id_warga, w.nama, w.alamat, w.no_hp)
        )
        if berhasil:
            self._list_warga.append(w)
        return berhasil

    def get_warga_list(self) -> List[Warga]:
        """Mengambil seluruh data warga dari list penyimpanan in-memory.

        Returns:
            List berisi semua objek Warga.
        """
        return list(self._list_warga)

    def cari_warga(self, id_warga: str) -> Optional[Warga]:
        """Mencari dan mengembalikan objek Warga berdasarkan ID.

        Parameter:
            id_warga: ID unik warga yang dicari.

        Returns:
            Objek Warga jika ditemukan, None jika tidak ada.
        """
        for w in self._list_warga:
            if w.id_warga == id_warga:
                return w
        return None

    # TODO
    def ubah_warga(self, w: Warga) -> bool:
        """Memperbarui data warga yang sudah tersimpan di list dan database.

        Parameter:
            w: Objek Warga dengan data yang sudah diperbarui.

        Returns:
            True jika pembaruan berhasil, False jika warga tidak ditemukan.
        """
        indeks = next(
            (i for i, x in enumerate(self._list_warga) if x.id_warga == w.id_warga), None
        )
        if indeks is None:
            return False
        query = "UPDATE warga SET nama=%s, alamat=%s, no_hp=%s WHERE id_warga=%s"
        berhasil = self._database_manager.simpan_data(
            query, (w.nama, w.alamat, w.no_hp, w.id_warga)
        )
        if berhasil:
            self._list_warga[indeks] = w
        return berhasil

    def hapus_warga(self, w: Warga) -> bool:
        """Menghapus objek warga dari list in-memory dan database.

        Parameter:
            w: Objek Warga yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika warga tidak ditemukan.
        """
        if not self.cari_warga(w.id_warga):
            return False
        berhasil = self._database_manager.hapus_data(
            "DELETE FROM warga WHERE id_warga=%s", (w.id_warga,)
        )
        if berhasil:
            self._list_warga = [x for x in self._list_warga if x.id_warga != w.id_warga]
        return berhasil

    # Fasilitas

    def tambah_fasilitas(self, f: Fasilitas) -> bool:
        """Menyimpan objek fasilitas baru ke list in-memory dan ke database.

        Parameter:
            f: Objek Fasilitas yang akan disimpan.

        Returns:
            True jika penyimpanan berhasil, False jika gagal.
        """
        query = (
            "INSERT INTO fasilitas (id_fasilitas, nama, harga_per_jam, deskripsi, status) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        berhasil = self._database_manager.simpan_data(
            query,
            (f.id_fasilitas, f.nama, f.harga_per_jam, f.deskripsi, f.status.value),
        )
        if berhasil:
            self._list_fasilitas.append(f)
        return berhasil

    def get_fasilitas_list(self) -> List[Fasilitas]:
        """Mengambil seluruh data fasilitas dari list penyimpanan in-memory.

        Returns:
            List berisi semua objek Fasilitas.
        """
        return list(self._list_fasilitas)

    def cari_fasilitas(self, id_fasilitas: str) -> Optional[Fasilitas]:
        """Mencari dan mengembalikan objek Fasilitas berdasarkan ID.

        Parameter:
            id_fasilitas: ID unik fasilitas yang dicari.

        Returns:
            Objek Fasilitas jika ditemukan, None jika tidak ada.
        """
        for f in self._list_fasilitas:
            if f.id_fasilitas == id_fasilitas:
                return f
        return None

    def ubah_fasilitas(self, f: Fasilitas) -> bool:
        """Memperbarui data fasilitas yang sudah tersimpan di list dan database.

        Parameter:
            f: Objek Fasilitas dengan data yang sudah diperbarui.

        Returns:
            True jika pembaruan berhasil, False jika fasilitas tidak ditemukan.
        """
        indeks = next(
            (i for i, x in enumerate(self._list_fasilitas) if x.id_fasilitas == f.id_fasilitas),
            None,
        )
        if indeks is None:
            return False
        query = (
            "UPDATE fasilitas SET nama=%s, harga_per_jam=%s, deskripsi=%s, status=%s "
            "WHERE id_fasilitas=%s"
        )
        berhasil = self._database_manager.simpan_data(
            query,
            (f.nama, f.harga_per_jam, f.deskripsi, f.status.value, f.id_fasilitas),
        )
        if berhasil:
            self._list_fasilitas[indeks] = f
        return berhasil

    def hapus_fasilitas(self, f: Fasilitas) -> bool:
        """Menghapus objek fasilitas dari list in-memory dan database.

        Parameter:
            f: Objek Fasilitas yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika fasilitas tidak ditemukan.
        """
        if not self.cari_fasilitas(f.id_fasilitas):
            return False
        berhasil = self._database_manager.hapus_data(
            "DELETE FROM fasilitas WHERE id_fasilitas=%s", (f.id_fasilitas,)
        )
        if berhasil:
            self._list_fasilitas = [
                x for x in self._list_fasilitas if x.id_fasilitas != f.id_fasilitas
            ]
        return berhasil

    # Reservasi

    def tambah_reservasi(self, r: Reservasi) -> bool:
        """Menambahkan reservasi ke list in-memory dan mengeksekusi INSERT ke database.

        Parameter:
            r: Objek Reservasi yang akan disimpan.

        Returns:
            True jika penyimpanan berhasil, False jika gagal.
        """
        pass

    # TODO
    def get_list_reservasi(self) -> List[Reservasi]:
        """Mengambil seluruh data reservasi dari list penyimpanan in-memory.

        Returns:
            List berisi semua objek Reservasi.
        """
        pass

    # TODO
    def cari_reservasi(self, id_reservasi: str) -> Optional[Reservasi]:
        """Mencari dan mengembalikan objek Reservasi berdasarkan ID.

        Parameter:
            id_reservasi: ID unik reservasi yang dicari.

        Returns:
            Objek Reservasi jika ditemukan, None jika tidak ada.
        """
        pass

    # TODO
    def cari_reservasi_by_fasilitas_by_tanggal(
        self, id_fasilitas: str, tanggal: date
    ) -> List[Reservasi]:
        """Mencari reservasi berdasarkan fasilitas dan tanggal untuk keperluan validasi jadwal.

        Parameter:
            id_fasilitas: ID fasilitas yang dicek jadwalnya.
            tanggal: Tanggal reservasi yang dicek.

        Returns:
            List Reservasi yang cocok dengan fasilitas dan tanggal tersebut.
        """
        pass

    # TODO
    def cari_reservasi_by_date_range(
        self, tanggal_mulai: date, tanggal_selesai: date
    ) -> List[Reservasi]:
        """Mencari reservasi dalam rentang tanggal tertentu untuk keperluan laporan.

        Parameter:
            tanggal_mulai: Tanggal awal rentang pencarian.
            tanggal_selesai: Tanggal akhir rentang pencarian.

        Returns:
            List Reservasi yang jatuh dalam rentang tanggal tersebut.
        """
        pass

    # TODO
    def cari_reservasi_by_fasilitas(self, id_fasilitas: str) -> List[Reservasi]:
        """Mencari seluruh riwayat reservasi berdasarkan fasilitas tertentu untuk laporan.

        Parameter:
            id_fasilitas: ID fasilitas yang riwayat reservasinya dicari.

        Returns:
            List semua Reservasi untuk fasilitas tersebut.
        """
        pass

    # TODO
    def update_status_reservasi(self, id_reservasi: str, status: StatusReservasi) -> bool:
        """Memperbarui status reservasi di list in-memory dan database.

        Parameter:
            id_reservasi: ID reservasi yang statusnya akan diperbarui.
            status: Status baru (BELUM_DIBAYAR atau LUNAS).

        Returns:
            True jika pembaruan berhasil, False jika reservasi tidak ditemukan.
        """
        pass

    # TODO
    def hapus_reservasi(self, r: Reservasi) -> bool:
        """Menghapus objek reservasi dari list in-memory dan database.

        Parameter:
            r: Objek Reservasi yang akan dihapus.

        Returns:
            True jika penghapusan berhasil, False jika reservasi tidak ditemukan.
        """
        pass

    # ------------------------------------------------------------- Notifikasi

    # TODO
    def tambah_notifikasi(self, n: Notifikasi) -> bool:
        """Menyimpan objek notifikasi baru ke list in-memory dan ke database.

        Parameter:
            n: Objek Notifikasi yang akan disimpan.

        Returns:
            True jika penyimpanan berhasil, False jika gagal.
        """
        pass

    # TODO
    def cari_notifikasi(self, id_notifikasi: str) -> Optional[Notifikasi]:
        """Mencari dan mengembalikan objek Notifikasi berdasarkan ID.

        Parameter:
            id_notifikasi: ID unik notifikasi yang dicari.

        Returns:
            Objek Notifikasi jika ditemukan, None jika tidak ada.
        """
        pass

    # TODO
    def get_list_notifikasi(self) -> List[Notifikasi]:
        """Mengambil seluruh data notifikasi dari list penyimpanan in-memory.

        Returns:
            List berisi semua objek Notifikasi.
        """
        pass
