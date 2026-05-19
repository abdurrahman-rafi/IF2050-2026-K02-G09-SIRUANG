from __future__ import annotations
import uuid
from datetime import date
from datetime import date as _date_type
from datetime import time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from src.entity.enums import StatusFasilitas, StatusReservasi
from src.entity.reservasi import Reservasi

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

    def get_jam_notifikasi(self) -> int:
        """Kembalikan nilai jam notifikasi saat ini dari NotifikasiController."""
        return self._notifikasi_controller.get_jam_notifikasi()

    # TODO
    def tambah_reservasi(
        self,
        id_warga: str,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
        jam_notifikasi_sebelum: int = 2,
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
        if tanggal < _date_type.today():
            return False

        fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
        if fasilitas is None or fasilitas.status == StatusFasilitas.MAINTENANCE:
            return False

        if self._data_repository.cek_tanggal_dalam_maintenance(id_fasilitas, tanggal):
            return False

        if not self.validasi_jadwal(id_fasilitas, tanggal, jam_mulai, jam_selesai):
            return False

        id_reservasi_baru = f"RES-{uuid.uuid4().hex[:6].upper()}"

        total_biaya = self.hitung_total_biaya(id_fasilitas, jam_mulai, jam_selesai)

        reservasi_baru = Reservasi(
            id_reservasi=id_reservasi_baru,
            id_warga=id_warga,
            id_fasilitas=id_fasilitas,
            tanggal_dibuat=tanggal,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            total_biaya=total_biaya,
            status=StatusReservasi.BELUM_DIBAYAR
        )

        self._data_repository.tambah_reservasi(reservasi_baru)
        self._notifikasi_controller.simpan_jam_sebelum(jam_notifikasi_sebelum)
        return True
        

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
        semua_reservasi = self._data_repository.get_list_reservasi()

        for res in semua_reservasi:
            if res.id_fasilitas == id_fasilitas and res.tanggal_dibuat == tanggal:
                if res.jam_mulai < jam_selesai and res.jam_selesai > jam_mulai:
                    return False
                
        return True        
        

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
        fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
        if fasilitas is None:
            return Decimal("0")
        harga_per_jam = fasilitas.harga_per_jam

        detik_mulai = (jam_mulai.hour * 3600) + (jam_mulai.minute * 60) + jam_mulai.second
        detik_selesai = (jam_selesai.hour * 3600) + (jam_selesai.minute * 60) + jam_selesai.second
        durasi_detik = detik_selesai - detik_mulai
        if durasi_detik < 0:
            durasi_detik += 86400
        durasi_jam = Decimal(str(durasi_detik)) / Decimal('3600')
        return durasi_jam * harga_per_jam
        

    # TODO
    def lihat_daftar_reservasi(self) -> List[Reservasi]:
        """Mengambil seluruh data reservasi dari DataRepository.

        Returns:
            List berisi semua objek Reservasi yang tersimpan.
        """
        return self._data_repository.get_list_reservasi()
        

    # TODO
    def buat_notifikasi(self, id_reservasi: str, pesan: str) -> Optional[Notifikasi]:
        """Mendelegasikan pembuatan notifikasi kepada NotifikasiController.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
            pesan: Isi pesan notifikasi yang akan dikirim.

        Returns:
            Objek Notifikasi yang berhasil dibuat, atau None jika gagal.
        """
        return self._notifikasi_controller.create_notifikasi(id_reservasi, pesan)
        
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
        semua_reservasi = self._data_repository.get_list_reservasi()
        reservasi_target = next((r for r in semua_reservasi if r.id_reservasi == id_reservasi), None)
        
        if not reservasi_target:
            return False
        
        if reservasi_target.status == StatusReservasi.LUNAS:
            return False

        if tanggal < _date_type.today():
            return False

        for res in semua_reservasi:
            if res.id_fasilitas == id_fasilitas and res.tanggal_dibuat == tanggal and res.id_reservasi != id_reservasi:
                if res.jam_mulai < jam_selesai and res.jam_selesai > jam_mulai:
                    return False
                
        berhasil_ubah = reservasi_target.ubah_data(id_warga, id_fasilitas, tanggal, jam_mulai, jam_selesai)

        if berhasil_ubah:
            fasilitas = self._data_repository.cari_fasilitas(id_fasilitas)
            harga_per_jam = fasilitas.harga_per_jam if fasilitas else Decimal("0")
            reservasi_target.hitung_total_biaya(harga_per_jam, jam_mulai, jam_selesai)
            self._data_repository.ubah_reservasi(reservasi_target)
            return True
        
        return False
        
