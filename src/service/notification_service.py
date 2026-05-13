from __future__ import annotations
import logging

from typing import TYPE_CHECKING, Callable, List, Optional, Set

from PyQt6.QtCore import QTimer

if TYPE_CHECKING:
    from src.controller.notifikasi_controller import NotifikasiController
    from src.entity.notifikasi import Notifikasi

INTERVAL_MS: int = 5 * 60 * 1000

logger = logging.getLogger(__name__)


class NotificationService:
    """Layanan scheduler dan distribusi notifikasi in-app (UC14).

    Bertanggung jawab untuk:
    - Menjalankan timer periodik yang memeriksa reservasi hampir berakhir.
    - Memanggil callback terdaftar saat notifikasi baru tiba (misalnya update badge).
    Penyimpanan notifikasi ke database dilakukan oleh NotifikasiController.
    """

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
        """Daftarkan callback yang dipanggil saat notifikasi baru masuk (mencegah duplikat)."""
        if fn not in self._on_notifikasi_baru:
            self._on_notifikasi_baru.append(fn)

    def start_scheduler(self) -> None:
        """Mulai background timer periodik."""
        try:
            self._timer.start()
            logger.debug("NotificationService scheduler started, interval=%s ms", self._timer.interval())
        except Exception:
            logger.exception("Gagal memulai scheduler NotificationService.")

    def stop_scheduler(self) -> None:
        """Hentikan timer saat aplikasi ditutup."""
        try:
            self._timer.stop()
            logger.debug("NotificationService scheduler stopped.")
        except Exception:
            logger.exception("Gagal menghentikan scheduler NotificationService.")

    def clear_sent_cache(self) -> None:
        """Reset cache _sudah_dikirim (berguna untuk testing atau saat data berubah)."""
        self._sudah_dikirim.clear()
        logger.debug("NotificationService sent cache cleared.")

    # ------------------------------------------------------------------
    # Internal timer callback
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Dipanggil otomatis tiap interval: cek reservasi yang hampir berakhir."""
        if self._notifikasi_controller is None:
            logger.debug("_tick: controller belum diset, dilewati.")
            return

        try:
            semua_reservasi = self._notifikasi_controller._data_repository.get_list_reservasi()
        except Exception:
            logger.exception("Gagal mengambil daftar reservasi dari repository.")
            return

        try:
            hampir_berakhir = self._notifikasi_controller.periksa_reservasi_akan_berakhir(semua_reservasi)
        except Exception:
            logger.exception("Error saat memeriksa reservasi hampir berakhir.")
            return

        for reservasi in hampir_berakhir:
            id_res = getattr(reservasi, "id_reservasi", None)
            if id_res is None:
                continue
            if id_res in self._sudah_dikirim:
                continue
            try:
                sent = self._notifikasi_controller.kirim_notifikasi(id_res)
                if sent is not None:
                    self._sudah_dikirim.add(id_res)
                    logger.debug("Notifikasi dikirim untuk reservasi %s", id_res)
            except Exception:
                logger.exception("Gagal memproses notifikasi untuk reservasi %s.", id_res)

    # ------------------------------------------------------------------
    # Public: fire callbacks (DB save is done by controller before calling this)
    # ------------------------------------------------------------------

    def kirim(self, notifikasi: Notifikasi) -> bool:
        """Panggil semua callback terdaftar untuk notifikasi yang baru dikirim.

        Catatan: penyimpanan ke database sudah dilakukan oleh NotifikasiController
        sebelum memanggil method ini.

        Returns:
            True selalu (callback errors dilog tapi tidak menghentikan eksekusi).
        """
        for fn in list(self._on_notifikasi_baru):
            try:
                fn(notifikasi)
            except Exception:
                logger.exception("Callback notifikasi baru gagal dieksekusi.")
        return True
