from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QMainWindow, QWidget

if TYPE_CHECKING:
    from src.controller.fasilitas_controller import FasilitasController
    from src.controller.laporan_controller import LaporanController
    from src.controller.notifikasi_controller import NotifikasiController
    from src.controller.reservasi_controller import ReservasiController
    from src.controller.warga_controller import WargaController


class MainWindow(QMainWindow):
    """Window utama aplikasi SIRUANG: navbar tetap dan routing antar halaman."""

    def __init__(
        self,
        warga_controller: WargaController,
        fasilitas_controller: FasilitasController,
        reservasi_controller: ReservasiController,
        laporan_controller: LaporanController,
        notifikasi_controller: NotifikasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._warga_controller: WargaController = warga_controller
        self._fasilitas_controller: FasilitasController = fasilitas_controller
        self._reservasi_controller: ReservasiController = reservasi_controller
        self._laporan_controller: LaporanController = laporan_controller
        self._notifikasi_controller: NotifikasiController = notifikasi_controller

    # TODO
    def setup_ui(self) -> None:
        """Menyiapkan tampilan awal window utama: navbar, area konten, dan judul aplikasi."""
        pass

    # TODO
    def setup_navbar(self) -> None:
        """Membuat dan mengkonfigurasi navbar tetap di atas dengan link navigasi dan ikon notifikasi."""
        pass

    # TODO
    def navigasi_ke_fasilitas(self) -> None:
        """Menampilkan halaman Daftar Fasilitas sebagai konten utama."""
        pass

    # TODO
    def navigasi_ke_warga(self) -> None:
        """Menampilkan halaman Daftar Warga sebagai konten utama."""
        pass

    # TODO
    def navigasi_ke_laporan(self) -> None:
        """Menampilkan halaman Laporan Reservasi sebagai konten utama."""
        pass

    # TODO
    def navigasi_ke_notifikasi(self) -> None:
        """Menampilkan panel atau halaman daftar notifikasi."""
        pass

    # TODO
    def perbarui_badge_notifikasi(self, jumlah_unread: int) -> None:
        """Memperbarui badge angka unread count pada ikon lonceng di navbar.

        Parameter:
            jumlah_unread: Jumlah notifikasi yang belum dibaca.
        """
        pass
