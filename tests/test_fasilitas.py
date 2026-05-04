import pytest


class TestFasilitasController:
    """Test suite untuk FasilitasController (UC05-UC08)."""

    # TODO
    def test_tambah_fasilitas_valid(self):
        """Menguji penambahan fasilitas dengan data yang valid harus berhasil."""
        pass

    # TODO
    def test_tambah_fasilitas_nama_kosong(self):
        """Menguji penambahan fasilitas dengan nama kosong harus gagal."""
        pass

    # TODO
    def test_tambah_fasilitas_harga_nol(self):
        """Menguji penambahan fasilitas dengan harga per jam 0 harus gagal."""
        pass

    # TODO
    def test_lihat_daftar_fasilitas(self):
        """Menguji pengambilan daftar fasilitas mengembalikan semua fasilitas tersimpan."""
        pass

    # TODO
    def test_lihat_detail_fasilitas_ditemukan(self):
        """Menguji pengambilan detail fasilitas berdasarkan ID yang ada."""
        pass

    # TODO
    def test_ubah_fasilitas_valid(self):
        """Menguji perubahan data fasilitas dengan data yang valid harus berhasil."""
        pass

    # TODO
    def test_hapus_fasilitas_tanpa_reservasi_aktif(self):
        """Menguji penghapusan fasilitas yang tidak memiliki reservasi BELUM_DIBAYAR harus berhasil."""
        pass

    # TODO
    def test_hapus_fasilitas_dengan_reservasi_aktif(self):
        """Menguji penghapusan fasilitas yang masih memiliki reservasi BELUM_DIBAYAR harus gagal."""
        pass

    # TODO
    def test_cek_reservasi_aktif_fasilitas_ada(self):
        """Menguji cek reservasi aktif fasilitas yang memiliki reservasi BELUM_DIBAYAR."""
        pass
