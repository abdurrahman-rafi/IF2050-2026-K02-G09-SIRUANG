import pytest


class TestNotifikasiController:
    """Test suite untuk NotifikasiController (UC14)."""

    # TODO
    def test_periksa_reservasi_akan_berakhir_ada(self):
        """Menguji deteksi reservasi yang waktu sewanya hampir habis mengembalikan list berisi data."""
        pass

    # TODO
    def test_periksa_reservasi_akan_berakhir_tidak_ada(self):
        """Menguji deteksi reservasi yang tidak ada yang akan berakhir mengembalikan list kosong."""
        pass

    # TODO
    def test_create_notifikasi_berhasil(self):
        """Menguji pembuatan notifikasi baru berhasil disimpan ke repository."""
        pass

    # TODO
    def test_sudah_dibaca_berhasil(self):
        """Menguji pembaruan status sudah_dibaca menjadi True berhasil."""
        pass

    # TODO
    def test_sudah_dibaca_notifikasi_tidak_ditemukan(self):
        """Menguji pembaruan status notifikasi yang tidak ada harus mengembalikan False."""
        pass

    # TODO
    def test_lihat_daftar_notifikasi(self):
        """Menguji pengambilan semua notifikasi mengembalikan seluruh data tersimpan."""
        pass
