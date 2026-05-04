from __future__ import annotations
from typing import TYPE_CHECKING, List

from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.fasilitas import Fasilitas


class FasilitasView(QWidget):
    """Tampilan pengelolaan data fasilitas: landing page, tambah, detail, edit, hapus (UC05-UC08)."""

    def __init__(
        self,
        data_repository: DataRepository,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._data_repository: DataRepository = data_repository

    # TODO
    def tampilkan_form_tambah_fasilitas(self) -> None:
        """Menampilkan dialog form input untuk menambahkan data fasilitas baru
        (nama, harga per jam, deskripsi, status awal)."""
        pass

    # TODO
    def tampilkan_daftar_fasilitas(self, daftar_fasilitas: List[Fasilitas]) -> None:
        """Menampilkan landing page daftar fasilitas dalam format card grid
        dengan fitur pencarian dan filter berdasarkan status.

        Parameter:
            daftar_fasilitas: List objek Fasilitas yang akan ditampilkan.
        """
        pass

    # TODO
    def tampilkan_detail_fasilitas(self, fasilitas: Fasilitas) -> None:
        """Menampilkan halaman detail fasilitas yang dipilih beserta form reservasi
        dan riwayat reservasi fasilitas tersebut.

        Parameter:
            fasilitas: Objek Fasilitas yang ingin ditampilkan detailnya.
        """
        pass

    # TODO
    def tampilkan_form_ubah_fasilitas(self, fasilitas: Fasilitas) -> None:
        """Menampilkan form edit dengan data fasilitas yang sudah ada sebagai nilai awal.

        Parameter:
            fasilitas: Objek Fasilitas yang datanya akan diubah.
        """
        pass

    # TODO
    def tampilkan_konfirmasi_hapus(self, fasilitas: Fasilitas) -> None:
        """Menampilkan dialog konfirmasi sebelum proses penghapusan fasilitas dijalankan.

        Parameter:
            fasilitas: Objek Fasilitas yang akan dihapus.
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
