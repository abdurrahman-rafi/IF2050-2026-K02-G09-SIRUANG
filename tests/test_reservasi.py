import pytest
from unittest.mock import MagicMock
from datetime import date, time
from decimal import Decimal

from src.controller.reservasi_controller import ReservasiController
from src.entity.reservasi import Reservasi
from src.entity.enums import StatusReservasi


def _buat_controller():
    mock_repo = MagicMock()
    mock_notif = MagicMock()
    return ReservasiController(mock_repo, mock_notif), mock_repo, mock_notif


def _dummy_reservasi(id_res="RES-DUMMY", id_fas="F-01", jam_mulai=time(10, 0), jam_selesai=time(12, 0),
                     status=StatusReservasi.BELUM_DIBAYAR):
    return Reservasi(id_res, "W-01", id_fas, date(2026, 5, 10), jam_mulai, jam_selesai,
                     Decimal('100000'), status)


def _mock_fasilitas(harga=Decimal('50000')):
    f = MagicMock()
    f.harga_per_jam = harga
    return f


class TestReservasiController:
    """Test suite untuk ReservasiController (UC09-UC11)."""

    def test_validasi_jadwal_tidak_bentrok(self):
        """Menguji validasi jadwal dengan slot waktu yang kosong harus lolos."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.validasi_jadwal("F-01", date(2026, 5, 10), time(13, 0), time(15, 0))
        assert hasil is True

    def test_validasi_jadwal_overlap_penuh(self):
        """Menguji validasi jadwal dengan waktu yang persis sama harus gagal (overlap)."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.validasi_jadwal("F-01", date(2026, 5, 10), time(10, 0), time(12, 0))
        assert hasil is False

    def test_validasi_jadwal_overlap_sebagian_kanan(self):
        """Menguji validasi jadwal dengan jam mulai baru di tengah reservasi yang ada harus gagal."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.validasi_jadwal("F-01", date(2026, 5, 10), time(11, 0), time(13, 0))
        assert hasil is False

    def test_validasi_jadwal_overlap_sebagian_kiri(self):
        """Menguji validasi jadwal dengan jam selesai baru melewati jam mulai reservasi yang ada harus gagal."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.validasi_jadwal("F-01", date(2026, 5, 10), time(9, 0), time(11, 0))
        assert hasil is False

    def test_validasi_jadwal_bersebelahan_tidak_overlap(self):
        """Menguji validasi jadwal dengan slot tepat setelah reservasi lain tidak dianggap overlap."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.validasi_jadwal("F-01", date(2026, 5, 10), time(12, 0), time(14, 0))
        assert hasil is True

    def test_hitung_total_biaya_benar(self):
        """Menguji perhitungan total biaya: durasi × harga_per_jam menghasilkan nilai yang benar."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.cari_fasilitas.return_value = _mock_fasilitas(Decimal('50000'))

        biaya = controller.hitung_total_biaya("F-01", time(10, 0), time(12, 0))
        assert biaya == Decimal('100000')

    def test_tambah_reservasi_jadwal_tersedia(self):
        """Menguji penambahan reservasi dengan jadwal yang tersedia harus berhasil."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = []
        mock_repo.cari_fasilitas.return_value = _mock_fasilitas()

        hasil = controller.tambah_reservasi("W-01", "F-01", date(2026, 5, 10), time(10, 0), time(12, 0))

        assert hasil is True
        mock_repo.tambah_reservasi.assert_called_once()

    def test_tambah_reservasi_jadwal_bentrok(self):
        """Menguji penambahan reservasi dengan jadwal yang bentrok harus gagal."""
        controller, mock_repo, _ = _buat_controller()
        mock_repo.get_list_reservasi.return_value = [_dummy_reservasi()]

        hasil = controller.tambah_reservasi("W-02", "F-01", date(2026, 5, 10), time(10, 0), time(12, 0))

        assert hasil is False
        mock_repo.tambah_reservasi.assert_not_called()

    def test_ubah_reservasi_status_belum_dibayar(self):
        """Menguji perubahan jadwal reservasi berstatus BELUM_DIBAYAR harus berhasil."""
        controller, mock_repo, _ = _buat_controller()
        dummy = _dummy_reservasi()
        mock_repo.get_list_reservasi.return_value = [dummy]
        mock_repo.cari_fasilitas.return_value = _mock_fasilitas()

        hasil = controller.ubah_reservasi("RES-DUMMY", "W-01", "F-01", date(2026, 5, 10), time(14, 0), time(16, 0))

        assert hasil is True
        mock_repo.ubah_reservasi.assert_called_once()

    def test_ubah_reservasi_status_lunas(self):
        """Menguji perubahan jadwal reservasi berstatus LUNAS harus gagal."""
        controller, mock_repo, _ = _buat_controller()
        dummy = _dummy_reservasi(status=StatusReservasi.LUNAS)
        mock_repo.get_list_reservasi.return_value = [dummy]

        hasil = controller.ubah_reservasi("RES-DUMMY", "W-01", "F-01", date(2026, 5, 10), time(14, 0), time(16, 0))

        assert hasil is False
        mock_repo.ubah_reservasi.assert_not_called()
