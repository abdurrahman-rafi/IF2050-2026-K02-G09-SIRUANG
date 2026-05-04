from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from src.controller.warga_controller import WargaController
    from src.data.data_repository import DataRepository


class WargaView(QWidget):
    """Tampilan pengelolaan data warga: daftar, tambah, detail, edit, dan hapus (UC01-UC04)."""

    def __init__(
        self,
        warga_controller: WargaController,
        data_repository: DataRepository,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._warga_controller: WargaController = warga_controller
        self._data_repository: DataRepository = data_repository

    # TODO
    def tampilkan_form_tambah_warga(self) -> None:
        """Menampilkan dialog form input data warga baru (nama, alamat, nomor HP)."""
        pass

    # TODO
    def tampilkan_daftar_warga(self) -> None:
        """Menampilkan halaman daftar warga dalam format tabel dengan fitur pencarian
        berdasarkan nama, alamat, atau nomor HP."""
        pass

    # TODO
    def tampilkan_detail_warga(self, id_warga: str) -> None:
        """Menampilkan halaman detail data satu warga berdasarkan ID.

        Parameter:
            id_warga: ID warga yang ingin ditampilkan detailnya.
        """
        pass

    # TODO
    def tampilkan_form_ubah_warga(self, id_warga: str) -> None:
        """Menampilkan form edit dengan data warga yang sudah ada sebagai nilai awal.

        Parameter:
            id_warga: ID warga yang datanya akan diubah.
        """
        pass

    # TODO
    def tampilkan_konfirmasi_hapus(self, id_warga: str) -> bool:
        """Menampilkan dialog konfirmasi sebelum proses penghapusan warga dijalankan.

        Parameter:
            id_warga: ID warga yang akan dihapus.

        Returns:
            True jika pengelola mengkonfirmasi penghapusan, False jika batal.
        """
        pass

    # TODO
    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses setelah operasi berhasil diproses.

        Parameter:
            pesan: Teks pesan sukses yang akan ditampilkan.
        """
        pass

    # TODO
    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error jika validasi atau operasi gagal.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        pass
