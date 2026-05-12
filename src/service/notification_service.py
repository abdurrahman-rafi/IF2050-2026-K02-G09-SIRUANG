from __future__ import annotations
from datetime import datetime
import logging

from typing import TYPE_CHECKING, Callable, List, Set, Optional
from PyQt6.QtCore import QTimer

if TYPE_CHECKING:
    from src.controller.notifikasi_controller import NotifikasiController
    from src.entity.notifikasi import Notifikasi

THRESHOLD_MENIT: int = 30
INTERVAL_MS: int = 5 * 60 * 1000 

logger = logging.getLogger(__name__)


class NotificationService:
    """Layanan pengiriman notifikasi in-app (UC 14)"""

    def __init__(self, interval_ms: int = INTERVAL_MS) -> None:
        self._sudah_dikirim: Set[str] = set()
        self._on_notifikasi_baru: List[Callable[[Notifikasi], None]] = []
        self._notifikasi_controller: Optional[NotifikasiController] = None

        self._timer = QTimer()
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._tick)

    def set_controller(self, controller: NotifikasiController) -> None:
        """Inject NotifikasiController setelah inisialisasi."""
        self._notifikasi_controller = controller

    def register_callback(self, fn: Callable[[Notifikasi], None]) -> None:
        """Daftarkan callback yang dipanggil saat notifikasi baru masuk.
        Menghindari pendaftaran duplikat.
        """
        if fn not in self._on_notifikasi_baru:
            self._on_notifikasi_baru.append(fn)

    def start_scheduler(self) -> None:
        """Mulai background timer"""
        try:
            self._timer.start()
            logger.debug("NotificationService scheduler started with interval %s ms", self._timer.interval())
        except Exception as e:
            logger.exception("Gagal memulai scheduler NotificationService: %s", e)

    def stop_scheduler(self) -> None:
        """Stop timer saat aplikasi ditutup"""
        try:
            self._timer.stop()
            logger.debug("NotificationService scheduler stopped")
        except Exception as e:
            logger.exception("Gagal menghentikan scheduler NotificationService: %s", e)

    def clear_sent_cache(self) -> None:
        """Reset cache _sudah_dikirim (berguna untuk testing atau saat data berubah)."""
        self._sudah_dikirim.clear()
        logger.debug("NotificationService sent cache cleared")

    def _tick(self) -> None:
        """Dipanggil otomatis tiap interval, cek reservasi hampir berakhir"""
        if self._notifikasi_controller is None:
            logger.debug("_tick called but controller not set; skipping")
            return

        try:
            semua_reservasi = self._notifikasi_controller._data_repository.get_list_reservasi()
        except Exception as e:
            logger.exception("Gagal mengambil daftar reservasi dari repository: %s", e)
            return

        try:
            hampir_berakhir = self._notifikasi_controller.periksa_reservasi_akan_berakhir(semua_reservasi)
        except Exception as e:
            logger.exception("Error saat memeriksa reservasi hampir berakhir: %s", e)
            return

        for reservasi in hampir_berakhir:
            try:
                id_res = getattr(reservasi, "id_reservasi", None)
                if id_res is None:
                    continue
                if id_res not in self._sudah_dikirim:
                    sent = self._notifikasi_controller.kirim_notifikasi(id_res)
                    if sent is not None:
                        self._sudah_dikirim.add(id_res)
                        logger.debug("Notifikasi dikirim untuk reservasi %s", id_res)
                    else:
                        logger.debug("kirim_notifikasi returned None for reservasi %s", id_res)
            except Exception as e:
                logger.exception("Gagal memproses reservasi %s dalam _tick: %s", getattr(reservasi, "id_reservasi", "<unknown>"), e)

    def kirim(self, notifikasi: Notifikasi) -> bool:
        """Simpan notifikasi ke DataRepository dan panggil callback.

        Returns True jika berhasil, False jika gagal.
        """
        if self._notifikasi_controller is None:
            logger.error("NotificationService.kirim dipanggil tetapi controller belum diset")
            return False

        try:
            self._notifikasi_controller._data_repository.tambah_notifikasi(notifikasi)
        except Exception as e:
            logger.exception("Gagal menyimpan notifikasi ke repository: %s", e)
            return False

        for fn in list(self._on_notifikasi_baru):
            try:
                fn(notifikasi)
            except Exception as e:
                logger.exception("Callback notifikasi baru gagal dieksekusi: %s", e)

        return True
