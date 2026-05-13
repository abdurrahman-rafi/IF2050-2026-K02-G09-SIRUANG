from __future__ import annotations
import logging

from typing import TYPE_CHECKING, Callable, List, Optional, Set

from PyQt6.QtCore import QTimer

if TYPE_CHECKING:
    from src.config.notification_config import NotificationConfig
    from src.controller.notifikasi_controller import NotifikasiController
    from src.entity.notifikasi import Notifikasi

_DEFAULT_INTERVAL_MS: int = 5 * 60 * 1000

logger = logging.getLogger(__name__)


class NotificationService:
    """Layanan scheduler dan distribusi notifikasi in-app (UC14).

    Bertanggung jawab untuk:
    - Menjalankan timer periodik yang memeriksa reservasi hampir berakhir.
    - Memanggil callback terdaftar saat notifikasi baru tiba (misalnya update badge).
    Penyimpanan notifikasi ke database dilakukan oleh NotifikasiController.
    """

    def __init__(
        self,
        config: Optional[NotificationConfig] = None,
        interval_ms: Optional[int] = None,
    ) -> None:
        self._sudah_dikirim: Set[str] = set()
        self._on_notifikasi_baru: List[Callable[[Notifikasi], None]] = []
        self._notifikasi_controller: Optional[NotifikasiController] = None

        if interval_ms is not None:
            resolved_ms = interval_ms
        elif config is not None:
            resolved_ms = config.notification_interval_minutes * 60 * 1000
        else:
            resolved_ms = _DEFAULT_INTERVAL_MS

        self._timer = QTimer()
        self._timer.setInterval(resolved_ms)
        self._timer.timeout.connect(self._tick)

    def set_controller(self, controller: NotifikasiController) -> None:
        """Inject NotifikasiController setelah inisialisasi."""
        self._notifikasi_controller = controller

    def register_callback(self, fn: Callable[[Notifikasi], None]) -> None:
        """Daftarkan callback yang dipanggil saat notifikasi baru masuk (mencegah duplikat)."""
        if fn not in self._on_notifikasi_baru:
            self._on_notifikasi_baru.append(fn)

    def start_scheduler(self) -> None:
        """Mulai background timer periodik dan langsung jalankan pengecekan pertama."""
        try:
            self._timer.start()
            # Cek langsung saat event loop mulai, tanpa menunggu interval pertama (5 menit)
            QTimer.singleShot(0, self._tick)
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

    def perbarui_interval(self, interval_ms: int) -> None:
        """Ubah interval scheduler; restart timer jika sedang berjalan."""
        was_active = self._timer.isActive()
        self._timer.stop()
        self._timer.setInterval(max(60_000, interval_ms))
        if was_active:
            self._timer.start()

    # ------------------------------------------------------------------
    # Internal timer callback
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Dipanggil otomatis tiap interval: cek reservasi yang hampir berakhir."""
        from datetime import datetime
        print(f"[SCHEDULER] _tick fired at {datetime.now().strftime('%H:%M:%S')}")

        if self._notifikasi_controller is None:
            print("[SCHEDULER] controller belum diset, dilewati.")
            return

        try:
            semua_reservasi = self._notifikasi_controller._data_repository.get_list_reservasi()
            print(f"[SCHEDULER] total reservasi di memory: {len(semua_reservasi)}")
            for r in semua_reservasi:
                print(f"  → id={r.id_reservasi}  tanggal={r.tanggal_dibuat}  selesai={r.jam_selesai}  status={r.status}")
        except Exception as e:
            print(f"[SCHEDULER] ERROR ambil reservasi: {e}")
            import traceback; traceback.print_exc()
            return

        try:
            hampir_berakhir = self._notifikasi_controller.periksa_reservasi_akan_berakhir(semua_reservasi)
            print(f"[SCHEDULER] hampir berakhir: {len(hampir_berakhir)}")
        except Exception as e:
            print(f"[SCHEDULER] ERROR periksa: {e}")
            import traceback; traceback.print_exc()
            return

        for reservasi in hampir_berakhir:
            id_res = getattr(reservasi, "id_reservasi", None)
            if id_res is None:
                continue
            if id_res in self._sudah_dikirim:
                print(f"[SCHEDULER] {id_res} sudah pernah dikirim, skip.")
                continue
            try:
                sent = self._notifikasi_controller.kirim_notifikasi(id_res)
                if sent is not None:
                    self._sudah_dikirim.add(id_res)
                    print(f"[SCHEDULER] notifikasi BERHASIL dikirim untuk {id_res}")
                else:
                    print(f"[SCHEDULER] kirim_notifikasi mengembalikan None untuk {id_res}")
            except Exception as e:
                print(f"[SCHEDULER] ERROR kirim notifikasi {id_res}: {e}")
                import traceback; traceback.print_exc()

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
