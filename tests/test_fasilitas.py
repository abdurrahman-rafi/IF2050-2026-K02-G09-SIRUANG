import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from src.controller.fasilitas_controller import FasilitasController
from src.entity.fasilitas import Fasilitas
from src.entity.fasilitas_maintenance import FasilitasMaintenance
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
        """Penambahan fasilitas dengan data valid mengembalikan ID baru dan memanggil repository."""
        mock_repo.tambah_fasilitas.return_value = True

        hasil = controller.tambah_fasilitas(
            "Lapangan Bola",
            Decimal("75000"),
            "Lapangan bola outdoor",
            StatusFasilitas.READY_TO_BOOK,
        )

        assert hasil is not None
        assert isinstance(hasil, str)
        mock_repo.tambah_fasilitas.assert_called_once()

    def test_tambah_fasilitas_nama_kosong(self, controller):
        """Penambahan fasilitas dengan nama kosong harus mengembalikan None."""
        hasil = controller.tambah_fasilitas(
            "", Decimal("50000"), "deskripsi", StatusFasilitas.READY_TO_BOOK
        )
        assert hasil is None

    def test_tambah_fasilitas_harga_nol(self, controller):
        """Penambahan fasilitas dengan harga 0 harus mengembalikan None."""
        hasil = controller.tambah_fasilitas(
            "Balai Warga", Decimal("0"), "deskripsi", StatusFasilitas.READY_TO_BOOK
        )
        assert hasil is None

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


class TestFasilitasMaintenance:
    """Test suite untuk manajemen jadwal maintenance fasilitas."""

    def test_set_maintenance_berhasil(self, controller, mock_repo):
        """set_maintenance harus menghapus record lama dan menyimpan record baru ke repository."""
        mock_repo.hapus_maintenance_by_fasilitas.return_value = True
        mock_repo.tambah_maintenance.return_value = True

        hasil = controller.set_maintenance(
            "f-001",
            date(2026, 6, 1),
            date(2026, 6, 14),
            "Perbaikan atap",
        )

        assert hasil is True
        mock_repo.hapus_maintenance_by_fasilitas.assert_called_once_with("f-001")
        mock_repo.tambah_maintenance.assert_called_once()
        record = mock_repo.tambah_maintenance.call_args[0][0]
        assert record.id_fasilitas == "f-001"
        assert record.tanggal_mulai == date(2026, 6, 1)
        assert record.tanggal_selesai == date(2026, 6, 14)
        assert record.keterangan == "Perbaikan atap"

    def test_set_maintenance_tanpa_keterangan(self, controller, mock_repo):
        """set_maintenance tanpa keterangan harus tetap berhasil dengan keterangan kosong."""
        mock_repo.hapus_maintenance_by_fasilitas.return_value = True
        mock_repo.tambah_maintenance.return_value = True

        controller.set_maintenance("f-001", date(2026, 6, 1), date(2026, 6, 14))

        record = mock_repo.tambah_maintenance.call_args[0][0]
        assert record.keterangan == ""

    def test_get_maintenance_aktif_ada(self, controller, mock_repo):
        """get_maintenance_aktif harus mengembalikan record pertama jika ada."""
        maint = FasilitasMaintenance("m-001", "f-001", date(2026, 6, 1), date(2026, 6, 14))
        mock_repo.get_maintenance_by_fasilitas.return_value = [maint]

        hasil = controller.get_maintenance_aktif("f-001")

        assert hasil is maint
        mock_repo.get_maintenance_by_fasilitas.assert_called_once_with("f-001")

    def test_get_maintenance_aktif_tidak_ada(self, controller, mock_repo):
        """get_maintenance_aktif harus mengembalikan None jika tidak ada record."""
        mock_repo.get_maintenance_by_fasilitas.return_value = []

        hasil = controller.get_maintenance_aktif("f-001")

        assert hasil is None

    def test_hapus_maintenance(self, controller, mock_repo):
        """hapus_maintenance harus mendelegasikan ke repository dengan ID fasilitas yang benar."""
        mock_repo.hapus_maintenance_by_fasilitas.return_value = True

        hasil = controller.hapus_maintenance("f-001")

        assert hasil is True
        mock_repo.hapus_maintenance_by_fasilitas.assert_called_once_with("f-001")

    def test_set_maintenance_mengganti_record_lama(self, controller, mock_repo):
        """set_maintenance harus menghapus record lama sebelum menyimpan yang baru."""
        mock_repo.hapus_maintenance_by_fasilitas.return_value = True
        mock_repo.tambah_maintenance.return_value = True

        controller.set_maintenance("f-001", date(2026, 6, 1), date(2026, 6, 14))
        controller.set_maintenance("f-001", date(2026, 7, 1), date(2026, 7, 31))

        assert mock_repo.hapus_maintenance_by_fasilitas.call_count == 2
        record = mock_repo.tambah_maintenance.call_args[0][0]
        assert record.tanggal_mulai == date(2026, 7, 1)