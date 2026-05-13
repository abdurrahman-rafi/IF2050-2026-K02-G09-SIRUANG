from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.notifikasi import Notifikasi
    from src.entity.reservasi import Reservasi
    from src.service.notification_service import NotificationService

THRESHOLD_MENIT: int = 30
logger = logging.getLogger(__name__)


class NotifikasiController:
    """Controller yang mengatur logika pemantauan jadwal dan pengiriman notifikasi (UC14)."""

    def __init__(
        self,
        data_repository: DataRepository,
        notification_service: NotificationService,
    ) -> None:
        self._data_repository: DataRepository = data_repository
        self._notification_service: NotificationService = notification_service

    def periksa_reservasi_akan_berakhir(
        self, list_reservasi: List[Reservasi]
    ) -> List[Reservasi]:
        """Memeriksa jadwal dan mengembalikan daftar reservasi yang waktu sewanya hampir habis.

        Parameter:
            list_reservasi: List semua reservasi aktif yang akan diperiksa.
        Returns:
            List Reservasi yang jam selesainya akan segera tiba.
        """
        hasil: List[Reservasi] = []
        sekarang = datetime.now()

        for reservasi in list_reservasi:
            jam_selesai: Optional[datetime] = getattr(reservasi, "jam_selesai", None)
            if jam_selesai is None:
                continue
            try:
                selisih_menit = (jam_selesai - sekarang).total_seconds() / 60
                if 0 < selisih_menit <= THRESHOLD_MENIT:
                    hasil.append(reservasi)
            except Exception:
                logger.exception("Gagal menghitung selisih waktu reservasi %s", getattr(reservasi, "id_reservasi", "?"))

        return hasil

    def kirim_notifikasi(self, id_reservasi: str) -> Optional[Notifikasi]:
        """Memanggil NotificationService untuk mengirimkan notifikasi in-app ke pengelola.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
        Returns:
            Objek Notifikasi yang berhasil dikirim, atau None jika gagal.
        """
        from src.entity.notifikasi import Notifikasi

        reservasi = self._data_repository.cari_reservasi(id_reservasi)
        if reservasi is None:
            return None

        pesan = (
            f"Reservasi akan segera berakhir!\n"
            f"Reservasi ID: {id_reservasi}\n"
            f"Jam Selesai: {reservasi.jam_selesai.strftime('%H:%M')}"
        )

        notifikasi = Notifikasi(
            id_notifikasi=str(uuid.uuid4()),
            id_reservasi=id_reservasi,
            pesan_notifikasi=pesan,
            waktu_kirim=datetime.now(),
            sudah_dibaca=False,
        )

        berhasil = self._notification_service.kirim(notifikasi)
        return notifikasi if berhasil else None

    def sudah_dibaca(self, id_notifikasi: str) -> bool:
        """Memperbarui atribut sudah_dibaca pada notifikasi menjadi True dan menyimpan ke database.

        Parameter:
            id_notifikasi: ID notifikasi yang akan ditandai sudah dibaca.
        Returns:
            True jika pembaruan berhasil, False jika notifikasi tidak ditemukan.
        """
        return self._data_repository.update_sudah_dibaca(id_notifikasi)

    def lihat_daftar_notifikasi(self) -> List[Notifikasi]:
        """Mengambil seluruh daftar notifikasi yang tersimpan di DataRepository.

        Returns:
            List berisi semua objek Notifikasi.
        """
        return self._data_repository.get_list_notifikasi()

    def create_notifikasi(self, id_reservasi: str, pesan: str) -> bool:
        """Mengatur logika pembuatan dan penyimpanan data notifikasi baru.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
            pesan: Isi pesan notifikasi.
        Returns:
            True jika notifikasi berhasil dibuat dan disimpan, False jika gagal.
        """
        from src.entity.notifikasi import Notifikasi

        notifikasi = Notifikasi(
            id_notifikasi=str(uuid.uuid4()),
            id_reservasi=id_reservasi,
            pesan_notifikasi=pesan,
            waktu_kirim=datetime.now(),
            sudah_dibaca=False,
        )
        return self._notification_service.kirim(notifikasi)