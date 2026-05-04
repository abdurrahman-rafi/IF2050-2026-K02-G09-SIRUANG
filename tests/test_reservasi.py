import pytest


class TestReservasiController:
    """Test suite untuk ReservasiController (UC09-UC11)."""

    # TODO
    def test_validasi_jadwal_tidak_bentrok(self):
        """Menguji validasi jadwal dengan slot waktu yang kosong harus lolos."""
        pass

    # TODO
    def test_validasi_jadwal_overlap_penuh(self):
        """Menguji validasi jadwal dengan waktu yang persis sama harus gagal (overlap)."""
        pass

    # TODO
    def test_validasi_jadwal_overlap_sebagian_kanan(self):
        """Menguji validasi jadwal dengan jam mulai baru di tengah reservasi yang ada harus gagal."""
        pass

    # TODO
    def test_validasi_jadwal_overlap_sebagian_kiri(self):
        """Menguji validasi jadwal dengan jam selesai baru melewati jam mulai reservasi yang ada harus gagal."""
        pass

    # TODO
    def test_validasi_jadwal_bersebelahan_tidak_overlap(self):
        """Menguji validasi jadwal dengan slot tepat setelah reservasi lain tidak dianggap overlap."""
        pass

    # TODO
    def test_hitung_total_biaya_benar(self):
        """Menguji perhitungan total biaya: durasi × harga_per_jam menghasilkan nilai yang benar."""
        pass

    # TODO
    def test_tambah_reservasi_jadwal_tersedia(self):
        """Menguji penambahan reservasi dengan jadwal yang tersedia harus berhasil."""
        pass

    # TODO
    def test_tambah_reservasi_jadwal_bentrok(self):
        """Menguji penambahan reservasi dengan jadwal yang bentrok harus gagal."""
        pass

    # TODO
    def test_ubah_reservasi_status_belum_dibayar(self):
        """Menguji perubahan jadwal reservasi berstatus BELUM_DIBAYAR harus berhasil."""
        pass

    # TODO
    def test_ubah_reservasi_status_lunas(self):
        """Menguji perubahan jadwal reservasi berstatus LUNAS harus gagal."""
        pass
