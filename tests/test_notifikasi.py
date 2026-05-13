import pytest
from datetime import date, datetime, time, timedelta
from unittest.mock import MagicMock

from src.controller.notifikasi_controller import NotifikasiController
from src.entity.enums import StatusReservasi


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_repo, mock_service):
    return NotifikasiController(mock_repo, mock_service)


def _buat_reservasi_mock(delta_menit: int, status=StatusReservasi.BELUM_DIBAYAR):
    """Buat reservasi mock dengan jam_selesai = sekarang + delta_menit."""
    target_dt = datetime.now() + timedelta(minutes=delta_menit)
    r = MagicMock()
    r.status = status
    r.tanggal_dibuat = target_dt.date()
    r.jam_selesai = target_dt.time()
    return r


class TestNotifikasiController:
    """Test suite untuk NotifikasiController (UC14)."""

    def test_periksa_reservasi_akan_berakhir_ada(self, controller):
        """Reservasi aktif yang berakhir dalam batas threshold harus terdeteksi."""
        # 15 menit ke depan — jauh di bawah default 2 jam
        reservasi_mock = _buat_reservasi_mock(delta_menit=15)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert len(hasil) == 1
        assert reservasi_mock in hasil

    def test_periksa_reservasi_akan_berakhir_tidak_ada(self, controller):
        """Reservasi yang sudah lewat tidak boleh masuk hasil deteksi."""
        reservasi_mock = _buat_reservasi_mock(delta_menit=-15)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert hasil == []

    def test_periksa_reservasi_akan_berakhir_lunas_diabaikan(self, controller):
        """Reservasi berstatus LUNAS tidak boleh menghasilkan notifikasi."""
        reservasi_mock = _buat_reservasi_mock(delta_menit=15, status=StatusReservasi.LUNAS)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert hasil == []

    def test_periksa_reservasi_akan_berakhir_jauh_di_depan(self, controller):
        """Reservasi yang masih berjam-jam ke depan (melebihi threshold) tidak masuk hasil."""
        # 5 jam ke depan, threshold default 2 jam → tidak memenuhi
        reservasi_mock = _buat_reservasi_mock(delta_menit=300)

        hasil = controller.periksa_reservasi_akan_berakhir([reservasi_mock])

        assert hasil == []

    def test_create_notifikasi_berhasil(self, controller, mock_service):
        """Pembuatan notifikasi baru harus berhasil disimpan ke repository dan mengembalikan True."""
        mock_service.kirim.return_value = True

        hasil = controller.create_notifikasi("r-001", "Reservasi hampir berakhir")

        assert hasil is True
        mock_service.kirim.assert_called_once()

    def test_sudah_dibaca_berhasil(self, controller, mock_repo):
        """Pembaruan status sudah_dibaca ke True harus berhasil."""
        mock_repo.update_sudah_dibaca.return_value = True

        hasil = controller.sudah_dibaca("n-001")

        assert hasil is True
        mock_repo.update_sudah_dibaca.assert_called_once_with("n-001")

    def test_sudah_dibaca_notifikasi_tidak_ditemukan(self, controller, mock_repo):
        """Pembaruan status notifikasi yang tidak ada harus mengembalikan False."""
        mock_repo.update_sudah_dibaca.return_value = False

        hasil = controller.sudah_dibaca("n-tidak-ada")

        assert hasil is False

    def test_lihat_daftar_notifikasi(self, controller, mock_repo):
        """Pengambilan daftar notifikasi harus memanggil repository dan mengembalikan data."""
        now = datetime.now()
        n1, n2 = MagicMock(), MagicMock()
        n1.waktu_kirim = now - timedelta(minutes=5)
        n2.waktu_kirim = now
        mock_repo.get_list_notifikasi.return_value = [n1, n2]

        hasil = controller.lihat_daftar_notifikasi()

        assert set(hasil) == {n1, n2}
        mock_repo.get_list_notifikasi.assert_called_once()

    def test_lihat_daftar_notifikasi_diurutkan_descending(self, controller, mock_repo):
        """Daftar notifikasi harus diurutkan terbaru di atas (descending waktu_kirim)."""
        now = datetime.now()
        n_lama = MagicMock()
        n_baru = MagicMock()
        n_lama.waktu_kirim = now - timedelta(hours=1)
        n_baru.waktu_kirim = now
        mock_repo.get_list_notifikasi.return_value = [n_lama, n_baru]

        hasil = controller.lihat_daftar_notifikasi()

        assert hasil[0] is n_baru
        assert hasil[1] is n_lama

    def test_lihat_daftar_notifikasi_dibatasi_max_display(self, mock_repo, mock_service):
        """Jumlah notifikasi yang dikembalikan tidak boleh melebihi notification_max_display."""
        from src.config.notification_config import NotificationConfig
        cfg = NotificationConfig()
        cfg.notification_max_display = 3

        ctrl = NotifikasiController(mock_repo, mock_service, cfg)

        now = datetime.now()
        mocks = []
        for i in range(5):
            m = MagicMock()
            m.waktu_kirim = now + timedelta(minutes=i)
            mocks.append(m)
        mock_repo.get_list_notifikasi.return_value = mocks

        hasil = ctrl.lihat_daftar_notifikasi()

        assert len(hasil) == 3
