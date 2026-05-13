from __future__ import annotations
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "notification.json"
_DEFAULTS: dict = {
    "notification_hours_before": 2,
    "notification_max_display": 10,
    "notification_interval_minutes": 5,
}


class NotificationConfig:
    """Konfigurasi notifikasi in-app: rentang waktu pengingat, batas tampilan, dan interval cek.

    Nilai disimpan dan dibaca dari config/notification.json.
    File dibuat otomatis dengan nilai default jika belum ada.
    """

    def __init__(self) -> None:
        self.notification_hours_before: int = _DEFAULTS["notification_hours_before"]
        self.notification_max_display: int = _DEFAULTS["notification_max_display"]
        self.notification_interval_minutes: int = _DEFAULTS["notification_interval_minutes"]
        self._muat()

    # ------------------------------------------------------------------
    # Internal load/save
    # ------------------------------------------------------------------

    def _muat(self) -> None:
        if not _CONFIG_PATH.exists():
            self._simpan()
            return
        try:
            with _CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.notification_hours_before = max(
                1, int(data.get("notification_hours_before", _DEFAULTS["notification_hours_before"]))
            )
            self.notification_max_display = max(
                1, int(data.get("notification_max_display", _DEFAULTS["notification_max_display"]))
            )
            self.notification_interval_minutes = max(
                1, int(data.get("notification_interval_minutes", _DEFAULTS["notification_interval_minutes"]))
            )
        except Exception:
            logger.exception("Gagal memuat konfigurasi notifikasi; menggunakan default.")

    def _simpan(self) -> None:
        try:
            _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with _CONFIG_PATH.open("w", encoding="utf-8") as f:
                json.dump(
                    {
                        "notification_hours_before": self.notification_hours_before,
                        "notification_max_display": self.notification_max_display,
                        "notification_interval_minutes": self.notification_interval_minutes,
                    },
                    f,
                    indent=2,
                )
        except Exception:
            logger.exception("Gagal menyimpan konfigurasi notifikasi.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def simpan(self, hours_before: int, max_display: int, interval_minutes: int = 5) -> None:
        """Perbarui nilai dan simpan ke file konfigurasi.

        Parameter:
            hours_before: Jumlah jam sebelum jam_selesai untuk mulai mengirim notifikasi (>= 1).
            max_display: Batas maksimum notifikasi yang ditampilkan di panel (>= 1).
            interval_minutes: Interval pengecekan scheduler dalam menit (>= 1).
        """
        self.notification_hours_before = max(1, hours_before)
        self.notification_max_display = max(1, max_display)
        self.notification_interval_minutes = max(1, interval_minutes)
        self._simpan()
