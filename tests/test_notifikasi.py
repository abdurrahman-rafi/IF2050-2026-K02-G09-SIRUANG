import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.controller.notifikasi_controller import NotifikasiController


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_repo, mock_service):
    return NotifikasiController(mock_repo, mock_service)


class TestNotifikasiController:
    """Test suite untuk NotifikasiController (UC14)."""

    def test_periksa_reservasi_akan_berakhir_ada(self, controller):
        """Menguji deteksi reservasi yang waktu sewanya hampir habis mengembalikan list berisi data."""
        reservasi_mock = MagicMock()
        reservasi_mock.jam_selesai = datetime.now() + timedelta(minutes=15)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert len(hasil) == 1
        assert reservasi_mock in hasil

    def test_periksa_reservasi_akan_berakhir_tidak_ada(self, controller):
        """Menguji deteksi reservasi yang tidak ada yang akan berakhir mengembalikan list kosong."""
        reservasi_mock = MagicMock()
        reservasi_mock.jam_selesai = datetime.now() - timedelta(minutes=15)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert hasil == []

    def test_create_notifikasi_berhasil(self, controller, mock_service):
        """Menguji pembuatan notifikasi baru berhasil disimpan ke repository."""
        mock_service.kirim.return_value = True

        hasil = controller.create_notifikasi("r-001", "Reservasi hampir berakhir")

        assert hasil is True
        mock_service.kirim.assert_called_once()

    def test_sudah_dibaca_berhasil(self, controller, mock_repo):
        """Menguji pembaruan status sudah_dibaca menjadi True berhasil."""
        mock_notifikasi = MagicMock()
        mock_repo.cari_notifikasi.return_value = mock_notifikasi

        hasil = controller.sudah_dibaca("n-001")

        assert hasil is True
        mock_notifikasi.tandai_sudah_dibaca.assert_called_once()

    def test_sudah_dibaca_notifikasi_tidak_ditemukan(self, controller, mock_repo):
        """Menguji pembaruan status notifikasi yang tidak ada harus mengembalikan False."""
        mock_repo.cari_notifikasi.return_value = None

        hasil = controller.sudah_dibaca("n-tidak-ada")

        assert hasil is False

    def test_lihat_daftar_notifikasi(self, controller, mock_repo):
        """Menguji pengambilan semua notifikasi mengembalikan seluruh data tersimpan."""
        mock_list = [MagicMock(), MagicMock()]
        mock_repo.get_list_notifikasi.return_value = mock_list

        hasil = controller.lihat_daftar_notifikasi()

        assert hasil == mock_list
        mock_repo.get_list_notifikasi.assert_called_once()
