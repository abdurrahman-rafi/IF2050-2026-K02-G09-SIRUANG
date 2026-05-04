from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.notifikasi import Notifikasi
    from src.entity.reservasi import Reservasi
    from src.service.notification_service import NotificationService


class NotifikasiController:
    """Controller yang mengatur logika pemantauan jadwal dan pengiriman notifikasi (UC14)."""

    def __init__(
        self,
        data_repository: DataRepository,
        notification_service: NotificationService,
    ) -> None:
        self._data_repository: DataRepository = data_repository
        self._notification_service: NotificationService = notification_service

    # TODO
    def periksa_reservasi_akan_berakhir(
        self, list_reservasi: List[Reservasi]
    ) -> List[Reservasi]:
        """Memeriksa jadwal dan mengembalikan daftar reservasi yang waktu sewanya hampir habis.

        Parameter:
            list_reservasi: List semua reservasi aktif yang akan diperiksa.

        Returns:
            List Reservasi yang jam selesainya akan segera tiba.
        """
        pass

    # TODO
    def kirim_notifikasi(self, id_reservasi: str) -> Optional[Notifikasi]:
        """Memanggil NotificationService untuk mengirimkan notifikasi in-app ke pengelola.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.

        Returns:
            Objek Notifikasi yang berhasil dikirim, atau None jika gagal.
        """
        pass

    # TODO
    def sudah_dibaca(self, id_notifikasi: str) -> bool:
        """Memperbarui atribut sudah_dibaca pada notifikasi menjadi True.

        Parameter:
            id_notifikasi: ID notifikasi yang akan ditandai sudah dibaca.

        Returns:
            True jika pembaruan berhasil, False jika notifikasi tidak ditemukan.
        """
        pass

    # TODO
    def lihat_daftar_notifikasi(self) -> List[Notifikasi]:
        """Mengambil seluruh daftar notifikasi yang tersimpan di DataRepository.

        Returns:
            List berisi semua objek Notifikasi.
        """
        pass

    # TODO
    def create_notifikasi(self, id_reservasi: str, pesan: str) -> bool:
        """Mengatur logika pembuatan dan penyimpanan data notifikasi baru.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
            pesan: Isi pesan notifikasi (berisi nama fasilitas, nama warga, dan jam selesai).

        Returns:
            True jika notifikasi berhasil dibuat dan disimpan, False jika gagal.
        """
        pass
