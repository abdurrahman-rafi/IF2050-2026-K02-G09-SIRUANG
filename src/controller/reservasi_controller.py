from __future__ import annotations
from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.controller.notifikasi_controller import NotifikasiController
    from src.data.data_repository import DataRepository
    from src.entity.notifikasi import Notifikasi
    from src.entity.reservasi import Reservasi


class ReservasiController:
    """Controller yang mengatur logika pencatatan dan pengelolaan reservasi (UC09-UC11)."""

    def __init__(
        self,
        data_repository: DataRepository,
        notifikasi_controller: NotifikasiController,
    ) -> None:
        self._data_repository: DataRepository = data_repository
        self._notifikasi_controller: NotifikasiController = notifikasi_controller

    # TODO
    def tambah_reservasi(
        self,
        id_warga: str,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
    ) -> bool:
        """Mencatat reservasi baru setelah memvalidasi jadwal, warga, dan fasilitas.

        Parameter:
            id_warga: ID warga yang melakukan reservasi.
            id_fasilitas: ID fasilitas yang dipesan.
            tanggal: Tanggal reservasi.
            jam_mulai: Jam mulai penggunaan fasilitas.
            jam_selesai: Jam selesai penggunaan fasilitas.

        Returns:
            True jika reservasi berhasil disimpan, False jika validasi gagal.
        """
        pass

    # TODO
    def validasi_jadwal(
        self,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
    ) -> bool:
        """Memeriksa apakah slot waktu yang dipilih tidak bentrok dengan reservasi yang ada.
        Overlap terjadi jika: existing.jam_mulai < jam_selesai AND existing.jam_selesai > jam_mulai.

        Parameter:
            id_fasilitas: ID fasilitas yang jadwalnya dicek.
            tanggal: Tanggal yang akan diperiksa.
            jam_mulai: Jam mulai yang akan diperiksa.
            jam_selesai: Jam selesai yang akan diperiksa.

        Returns:
            True jika slot waktu tersedia (tidak bentrok), False jika ada overlap.
        """
        pass

    # TODO
    def hitung_total_biaya(
        self, id_fasilitas: str, jam_mulai: time, jam_selesai: time
    ) -> Decimal:
        """Menghitung total biaya reservasi berdasarkan durasi dan harga per jam fasilitas.
        Rumus: durasi_jam × harga_per_jam.

        Parameter:
            id_fasilitas: ID fasilitas untuk mendapatkan harga per jam.
            jam_mulai: Jam mulai penggunaan.
            jam_selesai: Jam selesai penggunaan.

        Returns:
            Total biaya dalam Decimal (Rupiah).
        """
        pass

    # TODO
    def lihat_daftar_reservasi(self) -> List[Reservasi]:
        """Mengambil seluruh data reservasi dari DataRepository.

        Returns:
            List berisi semua objek Reservasi yang tersimpan.
        """
        pass

    # TODO
    def buat_notifikasi(self, id_reservasi: str, pesan: str) -> Optional[Notifikasi]:
        """Mendelegasikan pembuatan notifikasi kepada NotifikasiController.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
            pesan: Isi pesan notifikasi yang akan dikirim.

        Returns:
            Objek Notifikasi yang berhasil dibuat, atau None jika gagal.
        """
        pass

    # TODO
    def ubah_reservasi(
        self,
        id_reservasi: str,
        id_warga: str,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
    ) -> bool:
        """Mengubah jadwal reservasi yang berstatus BELUM_DIBAYAR setelah validasi jadwal baru.

        Parameter:
            id_reservasi: ID reservasi yang akan diubah.
            id_warga: ID warga (umumnya tidak berubah).
            id_fasilitas: ID fasilitas yang dipesan.
            tanggal: Tanggal baru reservasi.
            jam_mulai: Jam mulai baru.
            jam_selesai: Jam selesai baru.

        Returns:
            True jika perubahan berhasil, False jika status LUNAS atau jadwal bentrok.
        """
        pass
