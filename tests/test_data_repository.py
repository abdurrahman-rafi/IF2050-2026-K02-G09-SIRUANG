import pytest
from datetime import date, time, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from src.data.data_repository import DataRepository
from src.entity.enums import StatusFasilitas, StatusReservasi
from src.entity.fasilitas import Fasilitas
from src.entity.notifikasi import Notifikasi
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
def warga():
    return Warga("w-001", "Andi Pratama", "Jl. Merdeka 1", "08123456789")


@pytest.fixture
def fasilitas():
    return Fasilitas(
        "f-001", "Aula Serbaguna",
        Decimal("50000.00"), "Ruang serba guna",
        StatusFasilitas.READY_TO_BOOK,
    )


@pytest.fixture
def reservasi():
    return Reservasi(
        "r-001", "w-001", "f-001",
        date(2026, 5, 5),
        time(9, 0), time(11, 0),
        Decimal("100000.00"),
        StatusReservasi.BELUM_DIBAYAR,
    )


@pytest.fixture
def notifikasi():
    return Notifikasi(
        "n-001", "r-001",
        "Reservasi Anda akan berakhir dalam 1 jam.",
        datetime(2026, 5, 5, 8, 0, 0),
        False,
    )


class TestDataRepositoryInit:
    """Menguji inisialisasi DataRepository dan pemuatan data dari database."""

    def test_init_muat_data_dipanggil(self, mock_db):
        """Menguji _muat_data dipanggil saat init dan memanggil ambil_data untuk setiap tabel."""
        DataRepository(mock_db)
        assert mock_db.ambil_data.call_count == 4

    def test_init_list_kosong_jika_db_kosong(self, repo):
        """Menguji semua list in-memory kosong jika database tidak mengembalikan data."""
        assert repo.get_warga_list() == []
        assert repo.get_fasilitas_list() == []
        assert repo.get_list_reservasi() == []
        assert repo.get_list_notifikasi() == []


class TestDataRepositoryWarga:
    """Menguji operasi CRUD Warga pada DataRepository."""

    def test_tambah_warga_berhasil(self, repo, mock_db, warga):
        """Menguji tambah_warga menyimpan ke DB dan menambahkan ke list in-memory."""
        result = repo.tambah_warga(warga)
        assert result is True
        assert repo.cari_warga(warga.id_warga) is warga
        mock_db.simpan_data.assert_called_once()

    def test_tambah_warga_gagal_db_error(self, repo, mock_db, warga):
        """Menguji tambah_warga tidak menambah ke list jika DB gagal."""
        mock_db.simpan_data.return_value = False
        result = repo.tambah_warga(warga)
        assert result is False
        assert repo.cari_warga(warga.id_warga) is None

    def test_get_warga_list(self, repo, warga):
        """Menguji get_warga_list mengembalikan semua warga yang tersimpan."""
        repo.tambah_warga(warga)
        hasil = repo.get_warga_list()
        assert len(hasil) == 1
        assert hasil[0] is warga

    def test_cari_warga_ditemukan(self, repo, warga):
        """Menguji cari_warga mengembalikan objek Warga yang sesuai berdasarkan ID."""
        repo.tambah_warga(warga)
        assert repo.cari_warga(warga.id_warga) is warga

    def test_cari_warga_tidak_ditemukan(self, repo):
        """Menguji cari_warga mengembalikan None jika ID tidak ada di list."""
        assert repo.cari_warga("id-tidak-ada") is None

    def test_ubah_warga_berhasil(self, repo, mock_db, warga):
        """Menguji ubah_warga memperbarui data di list dan memanggil simpan_data."""
        repo.tambah_warga(warga)
        warga_baru = Warga(warga.id_warga, "Andi Diperbarui", "Jl. Baru 2", "08199999999")
        result = repo.ubah_warga(warga_baru)
        assert result is True
        assert repo.cari_warga(warga.id_warga).nama == "Andi Diperbarui"

    def test_ubah_warga_tidak_ditemukan(self, repo):
        """Menguji ubah_warga mengembalikan False jika warga tidak ada di list."""
        warga_asing = Warga("tidak-ada", "X", "Y", "0")
        assert repo.ubah_warga(warga_asing) is False

    def test_hapus_warga_berhasil(self, repo, mock_db, warga):
        """Menguji hapus_warga menghapus dari list dan memanggil hapus_data."""
        repo.tambah_warga(warga)
        result = repo.hapus_warga(warga)
        assert result is True
        assert repo.cari_warga(warga.id_warga) is None
        mock_db.hapus_data.assert_called_once()

    def test_hapus_warga_tidak_ditemukan(self, repo, warga):
        """Menguji hapus_warga mengembalikan False jika warga tidak ada di list."""
        assert repo.hapus_warga(warga) is False


class TestDataRepositoryFasilitas:
    """Menguji operasi CRUD Fasilitas pada DataRepository."""

    def test_tambah_fasilitas_berhasil(self, repo, mock_db, fasilitas):
        """Menguji tambah_fasilitas menyimpan ke DB dan menambahkan ke list."""
        result = repo.tambah_fasilitas(fasilitas)
        assert result is True
        assert repo.cari_fasilitas(fasilitas.id_fasilitas) is fasilitas

    def test_tambah_fasilitas_gagal_db_error(self, repo, mock_db, fasilitas):
        """Menguji tambah_fasilitas tidak menambah ke list jika DB gagal."""
        mock_db.simpan_data.return_value = False
        result = repo.tambah_fasilitas(fasilitas)
        assert result is False
        assert repo.cari_fasilitas(fasilitas.id_fasilitas) is None

    def test_get_fasilitas_list(self, repo, fasilitas):
        """Menguji get_fasilitas_list mengembalikan semua fasilitas yang tersimpan."""
        repo.tambah_fasilitas(fasilitas)
        assert len(repo.get_fasilitas_list()) == 1

    def test_cari_fasilitas_ditemukan(self, repo, fasilitas):
        """Menguji cari_fasilitas mengembalikan objek Fasilitas yang sesuai berdasarkan ID."""
        repo.tambah_fasilitas(fasilitas)
        assert repo.cari_fasilitas(fasilitas.id_fasilitas) is fasilitas

    def test_cari_fasilitas_tidak_ditemukan(self, repo):
        """Menguji cari_fasilitas mengembalikan None jika ID tidak ada."""
        assert repo.cari_fasilitas("tidak-ada") is None

    def test_ubah_fasilitas_berhasil(self, repo, fasilitas):
        """Menguji ubah_fasilitas memperbarui data fasilitas di list."""
        repo.tambah_fasilitas(fasilitas)
        fasilitas_baru = Fasilitas(
            fasilitas.id_fasilitas, "Aula Diperbarui",
            Decimal("75000.00"), "Deskripsi baru", StatusFasilitas.MAINTENANCE,
        )
        result = repo.ubah_fasilitas(fasilitas_baru)
        assert result is True
        assert repo.cari_fasilitas(fasilitas.id_fasilitas).nama == "Aula Diperbarui"

    def test_ubah_fasilitas_tidak_ditemukan(self, repo, fasilitas):
        """Menguji ubah_fasilitas mengembalikan False jika fasilitas tidak ada di list."""
        assert repo.ubah_fasilitas(fasilitas) is False

    def test_hapus_fasilitas_berhasil(self, repo, fasilitas):
        """Menguji hapus_fasilitas menghapus dari list dan memanggil hapus_data."""
        repo.tambah_fasilitas(fasilitas)
        result = repo.hapus_fasilitas(fasilitas)
        assert result is True
        assert repo.cari_fasilitas(fasilitas.id_fasilitas) is None

    def test_hapus_fasilitas_tidak_ditemukan(self, repo, fasilitas):
        """Menguji hapus_fasilitas mengembalikan False jika fasilitas tidak ada di list."""
        assert repo.hapus_fasilitas(fasilitas) is False


class TestDataRepositoryReservasi:
    """Menguji operasi CRUD dan query filter Reservasi pada DataRepository."""

    def test_tambah_reservasi_berhasil(self, repo, reservasi):
        """Menguji tambah_reservasi menyimpan ke DB dan menambahkan ke list."""
        result = repo.tambah_reservasi(reservasi)
        assert result is True
        assert repo.cari_reservasi(reservasi.id_reservasi) is reservasi

    def test_tambah_reservasi_gagal_db_error(self, repo, mock_db, reservasi):
        """Menguji tambah_reservasi tidak menambah ke list jika DB gagal."""
        mock_db.simpan_data.return_value = False
        result = repo.tambah_reservasi(reservasi)
        assert result is False
        assert repo.cari_reservasi(reservasi.id_reservasi) is None

    def test_get_list_reservasi(self, repo, reservasi):
        """Menguji get_list_reservasi mengembalikan semua reservasi yang tersimpan."""
        repo.tambah_reservasi(reservasi)
        assert len(repo.get_list_reservasi()) == 1

    def test_cari_reservasi_ditemukan(self, repo, reservasi):
        """Menguji cari_reservasi mengembalikan objek Reservasi yang sesuai berdasarkan ID."""
        repo.tambah_reservasi(reservasi)
        assert repo.cari_reservasi(reservasi.id_reservasi) is reservasi

    def test_cari_reservasi_tidak_ditemukan(self, repo):
        """Menguji cari_reservasi mengembalikan None jika ID tidak ada."""
        assert repo.cari_reservasi("tidak-ada") is None

    def test_cari_by_fasilitas_by_tanggal_cocok(self, repo, reservasi):
        """Menguji filter Q-002 mengembalikan reservasi yang sesuai fasilitas dan tanggal."""
        repo.tambah_reservasi(reservasi)
        hasil = repo.cari_reservasi_by_fasilitas_by_tanggal("f-001", date(2026, 5, 5))
        assert len(hasil) == 1
        assert hasil[0] is reservasi

    def test_cari_by_fasilitas_by_tanggal_tidak_cocok(self, repo, reservasi):
        """Menguji filter Q-002 mengembalikan list kosong jika tanggal berbeda."""
        repo.tambah_reservasi(reservasi)
        hasil = repo.cari_reservasi_by_fasilitas_by_tanggal("f-001", date(2026, 6, 1))
        assert hasil == []

    def test_cari_by_date_range_dalam_rentang(self, repo, reservasi):
        """Menguji filter Q-003 mengembalikan reservasi yang berada dalam rentang tanggal."""
        repo.tambah_reservasi(reservasi)
        hasil = repo.cari_reservasi_by_date_range(date(2026, 5, 1), date(2026, 5, 31))
        assert len(hasil) == 1

    def test_cari_by_date_range_diluar_rentang(self, repo, reservasi):
        """Menguji filter Q-003 mengembalikan list kosong jika reservasi di luar rentang."""
        repo.tambah_reservasi(reservasi)
        hasil = repo.cari_reservasi_by_date_range(date(2026, 6, 1), date(2026, 6, 30))
        assert hasil == []

    def test_cari_by_fasilitas(self, repo, reservasi):
        """Menguji filter Q-004 mengembalikan semua reservasi milik fasilitas tertentu."""
        repo.tambah_reservasi(reservasi)
        hasil = repo.cari_reservasi_by_fasilitas("f-001")
        assert len(hasil) == 1
        assert hasil[0] is reservasi

    def test_update_status_reservasi_berhasil(self, repo, mock_db, reservasi):
        """Menguji update_status_reservasi memperbarui status di list dan memanggil simpan_data (Q-005)."""
        repo.tambah_reservasi(reservasi)
        result = repo.update_status_reservasi(reservasi.id_reservasi, StatusReservasi.LUNAS)
        assert result is True
        assert repo.cari_reservasi(reservasi.id_reservasi).status == StatusReservasi.LUNAS

    def test_update_status_reservasi_tidak_ditemukan(self, repo):
        """Menguji update_status_reservasi mengembalikan False jika reservasi tidak ada."""
        assert repo.update_status_reservasi("tidak-ada", StatusReservasi.LUNAS) is False

    def test_hapus_reservasi_berhasil(self, repo, reservasi):
        """Menguji hapus_reservasi menghapus dari list dan memanggil hapus_data."""
        repo.tambah_reservasi(reservasi)
        result = repo.hapus_reservasi(reservasi)
        assert result is True
        assert repo.cari_reservasi(reservasi.id_reservasi) is None

    def test_hapus_reservasi_tidak_ditemukan(self, repo, reservasi):
        """Menguji hapus_reservasi mengembalikan False jika reservasi tidak ada di list."""
        assert repo.hapus_reservasi(reservasi) is False


class TestDataRepositoryNotifikasi:
    """Menguji operasi Notifikasi pada DataRepository."""

    def test_tambah_notifikasi_berhasil(self, repo, notifikasi):
        """Menguji tambah_notifikasi menyimpan ke DB dan menambahkan ke list."""
        result = repo.tambah_notifikasi(notifikasi)
        assert result is True
        assert repo.cari_notifikasi(notifikasi.id_notifikasi) is notifikasi

    def test_tambah_notifikasi_gagal_db_error(self, repo, mock_db, notifikasi):
        """Menguji tambah_notifikasi tidak menambah ke list jika DB gagal."""
        mock_db.simpan_data.return_value = False
        result = repo.tambah_notifikasi(notifikasi)
        assert result is False
        assert repo.cari_notifikasi(notifikasi.id_notifikasi) is None

    def test_cari_notifikasi_ditemukan(self, repo, notifikasi):
        """Menguji cari_notifikasi mengembalikan objek Notifikasi yang sesuai berdasarkan ID."""
        repo.tambah_notifikasi(notifikasi)
        assert repo.cari_notifikasi(notifikasi.id_notifikasi) is notifikasi

    def test_cari_notifikasi_tidak_ditemukan(self, repo):
        """Menguji cari_notifikasi mengembalikan None jika ID tidak ada."""
        assert repo.cari_notifikasi("tidak-ada") is None

    def test_get_list_notifikasi(self, repo, notifikasi):
        """Menguji get_list_notifikasi mengembalikan semua notifikasi yang tersimpan."""
        repo.tambah_notifikasi(notifikasi)
        assert len(repo.get_list_notifikasi()) == 1
