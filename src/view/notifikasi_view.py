from __future__ import annotations
from typing import TYPE_CHECKING, List

from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from src.controller.notifikasi_controller import NotifikasiController
    from src.entity.notifikasi import Notifikasi


class NotifikasiView(QWidget):
    """Tampilan notifikasi in-app: ikon lonceng, daftar notifikasi, dan tandai dibaca (UC14)."""

    def __init__(
        self,
        notifikasi_controller: NotifikasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._notifikasi_controller: NotifikasiController = notifikasi_controller

    # TODO
    def tampilkan_notifikasi(self, notifikasi: Notifikasi) -> None:
        """Menampilkan pop-up atau detail pesan notifikasi in-app kepada pengelola
        mengenai reservasi yang waktu sewanya akan segera berakhir.

        Parameter:
            notifikasi: Objek Notifikasi yang akan ditampilkan.
        """
        pass

    # TODO
    def tampilkan_daftar_notifikasi(self, list_notifikasi: List[Notifikasi]) -> None:
        """Menampilkan panel daftar riwayat notifikasi beserta status sudah/belum dibaca.

        Parameter:
            list_notifikasi: List objek Notifikasi yang akan ditampilkan.
        """
        pass
