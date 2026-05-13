from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from src.config.notification_config import NotificationConfig
from src.entity.enums import StatusReservasi

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.notifikasi import Notifikasi
    from src.entity.reservasi import Reservasi
    from src.service.notification_service import NotificationService

logger = logging.getLogger(__name__)


class NotifikasiController:
    """Controller yang mengatur logika pemantauan jadwal dan pengiriman notifikasi (UC14)."""

    def __init__(
        self,
        data_repository: DataRepository,
        notification_service: NotificationService,
        notification_config: Optional[NotificationConfig] = None,
    ) -> None:
        self._data_repository: DataRepository = data_repository
        self._notification_service: NotificationService = notification_service
        self._config: NotificationConfig = notification_config or NotificationConfig()

    # ------------------------------------------------------------------
    # Scheduler logic
    # ------------------------------------------------------------------

    def periksa_reservasi_akan_berakhir(
        self, list_reservasi: List[Reservasi]
    ) -> List[Reservasi]:
        """Kembalikan reservasi aktif yang jam_selesai-nya berada dalam rentang NOTIFICATION_HOURS_BEFORE jam ke depan.

        Parameter:
            list_reservasi: List semua reservasi yang akan diperiksa.
        Returns:
            List Reservasi yang memenuhi kriteria waktu.
        """
        hasil: List[Reservasi] = []
        sekarang = datetime.now()
        batas_detik = self._config.notification_hours_before * 3600

        for reservasi in list_reservasi:
            # Hanya reservasi yang masih aktif (belum dibayar / belum selesai)
            if getattr(reservasi, "status", None) == StatusReservasi.LUNAS:
                continue

            tanggal = getattr(reservasi, "tanggal_dibuat", None)
            jam_selesai_time = getattr(reservasi, "jam_selesai", None)
            if tanggal is None or jam_selesai_time is None:
                continue

            try:
                jam_selesai_dt = datetime.combine(tanggal, jam_selesai_time)
                selisih_detik = (jam_selesai_dt - sekarang).total_seconds()
                if 0 < selisih_detik <= batas_detik:
                    hasil.append(reservasi)
            except Exception:
                logger.exception(
                    "Gagal menghitung selisih waktu reservasi %s",
                    getattr(reservasi, "id_reservasi", "?"),
                )

        return hasil

    # ------------------------------------------------------------------
    # Notification creation
    # ------------------------------------------------------------------

    def kirim_notifikasi(self, id_reservasi: str) -> Optional[Notifikasi]:
        """Buat dan kirim notifikasi in-app pengingat untuk reservasi yang hampir berakhir.

        Format pesan: "Booking [ID_RESERVASI] akan segera berakhir dalam X jam."

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
        Returns:
            Objek Notifikasi yang berhasil dikirim, atau None jika gagal.
        """
        from src.entity.notifikasi import Notifikasi

        reservasi = self._data_repository.cari_reservasi(id_reservasi)
        if reservasi is None:
            print(f"[NOTIF] cari_reservasi({id_reservasi}) → tidak ditemukan")
            return None

        sekarang = datetime.now()
        try:
            jam_selesai_dt = datetime.combine(reservasi.tanggal_dibuat, reservasi.jam_selesai)
            sisa_jam = max(1, round((jam_selesai_dt - sekarang).total_seconds() / 3600))
        except Exception as e:
            print(f"[NOTIF] gagal hitung sisa jam: {e}")
            sisa_jam = self._config.notification_hours_before

        pesan = f"Booking {id_reservasi} akan segera berakhir dalam {sisa_jam} jam."
        print(f"[NOTIF] membuat notifikasi: {pesan}")

        notifikasi = Notifikasi(
            id_notifikasi=str(uuid.uuid4()),
            id_reservasi=id_reservasi,
            pesan_notifikasi=pesan,
            waktu_kirim=datetime.now(),
            sudah_dibaca=False,
        )

        ok = self.simpan_notifikasi(notifikasi)
        print(f"[NOTIF] simpan_notifikasi → {ok}")
        berhasil = self._notification_service.kirim(notifikasi)
        return notifikasi if berhasil else None

    def simpan_notifikasi(self, notifikasi: Notifikasi) -> bool:
        """Simpan notifikasi ke DataRepository.

        Dipanggil oleh NotificationService.kirim() untuk menghindari akses langsung
        ke _data_repository dari luar controller.

        Parameter:
            notifikasi: Objek Notifikasi yang akan disimpan.
        Returns:
            True jika berhasil.
        """
        try:
            ok = self._data_repository.tambah_notifikasi(notifikasi)
            if not ok:
                print(f"[NOTIF] tambah_notifikasi returned False untuk {notifikasi.id_notifikasi}")
            return ok
        except Exception as e:
            print(f"[NOTIF] EXCEPTION simpan_notifikasi: {e}")
            import traceback; traceback.print_exc()
            return False

    def sudah_dibaca(self, id_notifikasi: str) -> bool:
        """Tandai notifikasi sebagai sudah dibaca.

        Parameter:
            id_notifikasi: ID notifikasi yang akan ditandai sudah dibaca.
        Returns:
            True jika pembaruan berhasil, False jika notifikasi tidak ditemukan.
        """
        return self._data_repository.update_sudah_dibaca(id_notifikasi)

    def lihat_daftar_notifikasi(self) -> List[Notifikasi]:
        """Ambil daftar notifikasi terbaru, dibatasi oleh NOTIFICATION_MAX_DISPLAY.

        Returns:
            List notifikasi diurutkan descending waktu_kirim, maks NOTIFICATION_MAX_DISPLAY item.
        """
        semua = self._data_repository.get_list_notifikasi()
        try:
            semua_sorted = sorted(semua, key=lambda n: n.waktu_kirim, reverse=True)
        except Exception:
            semua_sorted = semua
        return semua_sorted[: self._config.notification_max_display]

    def create_notifikasi(self, id_reservasi: str, pesan: str) -> bool:
        """Buat dan simpan notifikasi baru dengan pesan kustom.

        Parameter:
            id_reservasi: ID reservasi yang menjadi subjek notifikasi.
            pesan: Isi pesan notifikasi.
        Returns:
            True jika notifikasi berhasil dibuat dan dikirim, False jika gagal.
        """
        from src.entity.notifikasi import Notifikasi

        notifikasi = Notifikasi(
            id_notifikasi=str(uuid.uuid4()),
            id_reservasi=id_reservasi,
            pesan_notifikasi=pesan,
            waktu_kirim=datetime.now(),
            sudah_dibaca=False,
        )
        self.simpan_notifikasi(notifikasi)
        return self._notification_service.kirim(notifikasi)
