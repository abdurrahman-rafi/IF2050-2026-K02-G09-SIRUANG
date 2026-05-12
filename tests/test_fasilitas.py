import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from src.controller.fasilitas_controller import FasilitasController
from src.entity.fasilitas import Fasilitas
from src.entity.enums import StatusFasilitas, StatusReservasi


@pytest.fixture
def mock_repo():
    """DataRepository palsu (mock) untuk testing tanpa database sungguhan."""
    return MagicMock()


@pytest.fixture
def controller(mock_repo):
    return FasilitasController(mock_repo)


@pytest.fixture
def fasilitas_contoh():
    return Fasilitas(
        id_fasilitas="f-001",
        nama="Balai Warga",
        harga_per_jam=Decimal("50000"),
        deskripsi="Balai warga komunitas RW 03",
        status=StatusFasilitas.READY_TO_BOOK,
    )


def _buat_reservasi_mock(id_fasilitas: str, status: StatusReservasi) -> MagicMock:
    """Helper membuat objek reservasi palsu."""
    r = MagicMock()
    r.id_fasilitas = id_fasilitas
    r.status = status
    return r


class TestFasilitasController:
    """Test suite untuk FasilitasController (UC05-UC08)."""

    def test_tambah_fasilitas_valid(self, controller, mock_repo):
        """Penambahan fasilitas dengan data valid harus berhasil dan memanggil repository."""
        mock_repo.tambah_fasilitas.return_value = True

        hasil = controller.tambah_fasilitas(
            "Lapangan Bola",
            Decimal("75000"),
            "Lapangan bola outdoor",
            StatusFasilitas.READY_TO_BOOK,
        )

        assert hasil is True
        mock_repo.tambah_fasilitas.assert_called_once()

    def test_tambah_fasilitas_nama_kosong(self, controller):
        """Penambahan fasilitas dengan nama kosong harus gagal tanpa memanggil repository."""
        hasil = controller.tambah_fasilitas(
            "", Decimal("50000"), "deskripsi", StatusFasilitas.READY_TO_BOOK
        )
        assert hasil is False

    def test_tambah_fasilitas_harga_nol(self, controller):
        """Penambahan fasilitas dengan harga 0 harus gagal."""
        hasil = controller.tambah_fasilitas(
            "Balai Warga", Decimal("0"), "deskripsi", StatusFasilitas.READY_TO_BOOK
        )
        assert hasil is False

    def test_lihat_daftar_fasilitas(self, controller, mock_repo, fasilitas_contoh):
        """Pengambilan daftar fasilitas harus mengembalikan semua fasilitas dari repository."""
        mock_repo.get_fasilitas_list.return_value = [fasilitas_contoh]

        hasil = controller.lihat_daftar_fasilitas()

        assert len(hasil) == 1
        assert hasil[0].nama == "Balai Warga"
        mock_repo.get_fasilitas_list.assert_called_once()

    def test_lihat_detail_fasilitas_ditemukan(self, controller, mock_repo, fasilitas_contoh):
        """Pengambilan detail fasilitas dengan ID yang ada harus mengembalikan objek Fasilitas."""
        mock_repo.cari_fasilitas.return_value = fasilitas_contoh

        hasil = controller.lihat_detail_fasilitas("f-001")

        assert hasil is not None
        assert hasil.id_fasilitas == "f-001"
        mock_repo.cari_fasilitas.assert_called_once_with("f-001")

    def test_ubah_fasilitas_valid(self, controller, mock_repo, fasilitas_contoh):
        """Perubahan data fasilitas dengan data valid dan ID yang ada harus berhasil."""
        mock_repo.cari_fasilitas.return_value = fasilitas_contoh
        mock_repo.ubah_fasilitas.return_value = True

        hasil = controller.ubah_fasilitas(
            "f-001",
            "Balai Warga Renovasi",
            Decimal("60000"),
            "Sudah direnovasi",
            StatusFasilitas.READY_TO_BOOK,
        )

        assert hasil is True
        assert fasilitas_contoh.nama == "Balai Warga Renovasi"
        mock_repo.ubah_fasilitas.assert_called_once_with(fasilitas_contoh)

    def test_hapus_fasilitas_tanpa_reservasi_aktif(self, controller, mock_repo, fasilitas_contoh):
        """Penghapusan fasilitas tanpa reservasi BELUM_DIBAYAR harus berhasil."""
        mock_repo.get_list_reservasi.return_value = []
        mock_repo.cari_fasilitas.return_value = fasilitas_contoh
        mock_repo.hapus_fasilitas.return_value = True

        hasil = controller.hapus_fasilitas("f-001")

        assert hasil is True
        mock_repo.hapus_fasilitas.assert_called_once_with(fasilitas_contoh)

    def test_hapus_fasilitas_dengan_reservasi_aktif(self, controller, mock_repo):
        """Penghapusan fasilitas yang masih punya reservasi BELUM_DIBAYAR harus gagal."""
        reservasi = _buat_reservasi_mock("f-001", StatusReservasi.BELUM_DIBAYAR)
        mock_repo.get_list_reservasi.return_value = [reservasi]

        hasil = controller.hapus_fasilitas("f-001")

        assert hasil is False
        mock_repo.hapus_fasilitas.assert_not_called()

    def test_cek_reservasi_aktif_fasilitas_ada(self, controller, mock_repo):
        """Cek reservasi aktif harus return True jika ada reservasi BELUM_DIBAYAR."""
        reservasi = _buat_reservasi_mock("f-001", StatusReservasi.BELUM_DIBAYAR)
        mock_repo.get_list_reservasi.return_value = [reservasi]

        hasil = controller.cek_reservasi_aktif_fasilitas("f-001")

        assert hasil is True