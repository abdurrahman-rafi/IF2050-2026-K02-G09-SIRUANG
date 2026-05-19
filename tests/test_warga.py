from datetime import date, time
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from src.controller.warga_controller import WargaController
from src.data.data_repository import DataRepository
from src.entity.enums import StatusReservasi
from src.entity.reservasi import Reservasi
from src.entity.warga import Warga


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.ambil_data.return_value = []
    db.simpan_data.return_value = True
    db.hapus_data.return_value = True
    return db


@pytest.fixture
def repo(mock_db):
    return DataRepository(mock_db)


@pytest.fixture
def controller(repo):
    return WargaController(repo)


@pytest.fixture
def warga():
    return Warga("w-001", "Andi Pratama", "Jl. Merdeka 1", "08123456789")


def buat_reservasi(id_warga: str, status: StatusReservasi) -> Reservasi:
    return Reservasi(
        "r-001",
        id_warga,
        "f-001",
        date(2026, 5, 5),
        time(9, 0),
        time(11, 0),
        Decimal("100000.00"),
        status,
    )


class TestWargaEntity:
    """Test suite untuk entity Warga."""

    def test_validate_data_valid(self):
        warga = Warga("w-001", "Andi", "Jl. Merdeka 1", "08123456789")

        assert warga.validate_data() is True

    def test_validate_data_nama_kosong(self):
        warga = Warga("w-001", "", "Jl. Merdeka 1", "08123456789")

        assert warga.validate_data() is False

    def test_validate_data_no_hp_tidak_valid(self):
        warga = Warga("w-001", "Andi", "Jl. Merdeka 1", "08123abc789")

        assert warga.validate_data() is False


class TestWargaController:
    """Test suite untuk WargaController (UC01-UC04)."""

    def test_tambah_warga_valid(self, controller, repo):
        result = controller.tambah_warga("Andi Pratama", "Jl. Merdeka 1", "08123456789")

        daftar_warga = repo.get_warga_list()
        assert result is True
        assert len(daftar_warga) == 1
        assert daftar_warga[0].nama == "Andi Pratama"
        UUID(daftar_warga[0].id_warga)

    def test_tambah_warga_nama_kosong(self, controller, repo, mock_db):
        result = controller.tambah_warga("", "Jl. Merdeka 1", "08123456789")

        assert result is False
        assert repo.get_warga_list() == []
        mock_db.simpan_data.assert_not_called()

    def test_tambah_warga_no_hp_tidak_valid(self, controller, repo, mock_db):
        result = controller.tambah_warga("Andi", "Jl. Merdeka 1", "08123abc789")

        assert result is False
        assert repo.get_warga_list() == []
        mock_db.simpan_data.assert_not_called()

    def test_lihat_daftar_warga(self, controller, repo, warga):
        repo.tambah_warga(warga)

        hasil = controller.lihat_daftar_warga()

        assert hasil == [warga]

    def test_lihat_detail_warga_ditemukan(self, controller, repo, warga):
        repo.tambah_warga(warga)

        hasil = controller.lihat_detail_warga(warga.id_warga)

        assert hasil is warga

    def test_lihat_detail_warga_tidak_ditemukan(self, controller):
        assert controller.lihat_detail_warga("id-tidak-ada") is None

    def test_ubah_warga_valid(self, controller, repo, warga):
        repo.tambah_warga(warga)

        result = controller.ubah_warga(
            warga.id_warga,
            "Andi Diperbarui",
            "Jl. Baru 2",
            "08199999999",
        )

        warga_terbaru = repo.cari_warga(warga.id_warga)
        assert result is True
        assert warga_terbaru is not None
        assert warga_terbaru.nama == "Andi Diperbarui"
        assert warga_terbaru.alamat == "Jl. Baru 2"
        assert warga_terbaru.no_hp == "08199999999"

    def test_ubah_warga_no_hp_tidak_valid(self, controller, repo, warga):
        repo.tambah_warga(warga)

        result = controller.ubah_warga(warga.id_warga, "Andi", "Jl. Baru", "08123abc")

        warga_tetap = repo.cari_warga(warga.id_warga)
        assert result is False
        assert warga_tetap is warga
        assert warga_tetap.nama == "Andi Pratama"

    def test_hapus_warga_tanpa_reservasi_aktif(self, controller, repo, warga):
        repo.tambah_warga(warga)

        result = controller.hapus_warga(warga.id_warga)

        assert result is True
        assert repo.cari_warga(warga.id_warga) is None

    def test_hapus_warga_dengan_reservasi_aktif(self, controller, repo, warga):
        repo.tambah_warga(warga)
        repo.tambah_reservasi(buat_reservasi(warga.id_warga, StatusReservasi.BELUM_DIBAYAR))

        result = controller.hapus_warga(warga.id_warga)

        assert result is False
        assert repo.cari_warga(warga.id_warga) is warga

    def test_hapus_warga_dengan_reservasi_lunas(self, controller, repo, warga):
        repo.tambah_warga(warga)
        repo.tambah_reservasi(buat_reservasi(warga.id_warga, StatusReservasi.LUNAS))

        result = controller.hapus_warga(warga.id_warga)

        assert result is True
        assert repo.cari_warga(warga.id_warga) is None

    def test_hapus_warga_reservasi_lunas_id_warga_jadi_null(self, controller, repo, warga):
        """Setelah warga dengan reservasi LUNAS dihapus, id_warga di reservasi harus jadi None."""
        repo.tambah_warga(warga)
        reservasi = buat_reservasi(warga.id_warga, StatusReservasi.LUNAS)
        repo.tambah_reservasi(reservasi)

        controller.hapus_warga(warga.id_warga)

        assert reservasi.id_warga is None

    def test_hapus_warga_data_reservasi_lunas_tetap_ada(self, controller, repo, warga):
        """Setelah warga dihapus, data reservasi LUNAS tetap tersimpan di repository."""
        repo.tambah_warga(warga)
        reservasi = buat_reservasi(warga.id_warga, StatusReservasi.LUNAS)
        repo.tambah_reservasi(reservasi)
        id_res = reservasi.id_reservasi

        controller.hapus_warga(warga.id_warga)

        semua = repo.get_list_reservasi()
        assert len(semua) == 1
        assert semua[0].id_reservasi == id_res
        assert semua[0].id_warga is None

    def test_hapus_warga_beberapa_reservasi_lunas_semua_jadi_null(self, controller, repo, warga):
        """Semua reservasi LUNAS milik warga yang dihapus harus memiliki id_warga None."""
        repo.tambah_warga(warga)
        res1 = Reservasi("r-001", warga.id_warga, "f-001", date(2026, 3, 1), time(9, 0), time(11, 0), Decimal("100000"), StatusReservasi.LUNAS)
        res2 = Reservasi("r-002", warga.id_warga, "f-001", date(2026, 3, 2), time(13, 0), time(15, 0), Decimal("100000"), StatusReservasi.LUNAS)
        repo.tambah_reservasi(res1)
        repo.tambah_reservasi(res2)

        controller.hapus_warga(warga.id_warga)

        assert res1.id_warga is None
        assert res2.id_warga is None
        assert len(repo.get_list_reservasi()) == 2

    def test_cek_reservasi_aktif_warga_ada(self, controller, repo, warga):
        repo.tambah_warga(warga)
        repo.tambah_reservasi(buat_reservasi(warga.id_warga, StatusReservasi.BELUM_DIBAYAR))

        assert controller.cek_reservasi_aktif_warga(warga.id_warga) is True

    def test_cek_reservasi_aktif_warga_tidak_ada(self, controller, repo, warga):
        repo.tambah_warga(warga)

        assert controller.cek_reservasi_aktif_warga(warga.id_warga) is False
