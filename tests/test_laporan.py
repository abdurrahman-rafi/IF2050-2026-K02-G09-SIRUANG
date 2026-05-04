import pytest


class TestLaporanController:
    """Test suite untuk LaporanController (UC12-UC13)."""

    # TODO
    def test_lihat_riwayat_per_waktu_ada_data(self):
        """Menguji pengambilan riwayat reservasi dalam rentang tanggal yang memiliki data."""
        pass

    # TODO
    def test_lihat_riwayat_per_waktu_kosong(self):
        """Menguji pengambilan riwayat reservasi dalam rentang tanggal tanpa data mengembalikan list kosong."""
        pass

    # TODO
    def test_lihat_riwayat_per_fasilitas_ada_data(self):
        """Menguji pengambilan riwayat reservasi berdasarkan fasilitas yang memiliki data."""
        pass

    # TODO
    def test_lihat_riwayat_per_fasilitas_kosong(self):
        """Menguji pengambilan riwayat reservasi fasilitas tanpa data mengembalikan list kosong."""
        pass

    # TODO
    def test_hitung_total_pendapatan_hanya_lunas(self):
        """Menguji total pendapatan hanya menjumlahkan reservasi berstatus LUNAS."""
        pass

    # TODO
    def test_hitung_total_pendapatan_semua_belum_dibayar(self):
        """Menguji total pendapatan mengembalikan 0 jika semua reservasi BELUM_DIBAYAR."""
        pass

    # TODO
    def test_hitung_total_pendapatan_list_kosong(self):
        """Menguji total pendapatan mengembalikan Decimal('0') jika list kosong."""
        pass
