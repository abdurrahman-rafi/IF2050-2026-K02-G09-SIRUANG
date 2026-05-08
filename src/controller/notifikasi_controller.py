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
        hasil: list[Reservasi] = []
        sekarang = datetime.now()

        for reservasi in list_reservasi:
            jam_selesai: Optional[datetime] = getattr(reservasi, "jam_selesai", None)
            if jam_selesai is None:
                continue

            try:
                selisih_menit = (jam_selesai - sekarang).total_seconds() / 60
            except Exception as e:
                logger.exception("Gagal menghitung selisih waktu untuk reservasi %s: %s", getattr(reserv