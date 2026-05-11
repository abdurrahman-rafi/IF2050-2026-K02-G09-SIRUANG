import pytest


class TestWargaController:
    """Test suite untuk WargaController (UC01-UC04)."""

    # TODO
    def test_tambah_warga_valid(self):
        """Menguji penambahan warga dengan data yang valid harus berhasil."""
        pass

    # TODO
    def test_tambah_warga_nama_kosong(self):
        """Menguji penambahan warga dengan nama kosong harus gagal."""
        pass

    # TODO
    def test_tambah_warga_no_hp_tidak_valid(self):
        """Menguji penambahan warga dengan nomor HP berisi huruf harus gagal."""
        pass

    # TODO
    def test_lihat_daftar_warga(self):
        """Menguji pengambilan daftar warga mengembalikan semua warga tersimpan."""
        pass

    # TODO
    def test_lihat_detail_warga_ditemukan(self):
        """Menguji pengambilan detail warga berdasarkan ID yang ada."""
        pass

    # TODO
    def test_lihat_detail_warga_tidak_ditemukan(self):
        """Menguji pengambilan detail warga dengan ID yang tidak ada harus mengembalikan None."""
        pass

    # TODO
    def test_ubah_warga_valid(self):
        """Menguji perubahan data warga dengan data yang valid harus berhasil."""
        pass

    # TODO
    def test_hapus_warga_tanpa_reservasi_aktif(self):
        """Menguji penghapusan warga yang tidak memiliki reservasi BELUM_DIBAYAR harus berhasil."""
        pass

    # TODO
    def test_hapus_warga_dengan_reservasi_aktif(self):
        """Menguji penghapusan warga yang masih memiliki reservasi BELUM_DIBAYAR harus gagal."""
        pass

    # TODO
    def test_cek_reservasi_aktif_warga_ada(self):
        """Menguji cek reservasi aktif warga yang memiliki reservasi BELUM_DIBAYAR."""
        pass

    # TODO
    def test_cek_reservasi_aktif_warga_tidak_ada(self):
        """Menguji cek reservasi aktif warga yang tidak memiliki reservasi BELUM_DIBAYAR."""
        pass
