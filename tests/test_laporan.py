import pytest
from datetime import date, time
from decimal import Decimal
from unittest.mock import MagicMock

from src.controller.laporan_controller import LaporanController
from src.entity.enums import StatusReservasi
from src.entity.reservasi import Reservasi


def _buat_reservasi(
    id_reservasi: str,
    id_fasilitas: str,
    tanggal: date,
    status: StatusReservasi,
    total_biaya: Decimal = Decimal("100000"),
) -> Reservasi:
    return Reservasi(
        id_reservasi, "w-001", id_fasilitas,
        tanggal,
        time(9, 0), time(11, 0),
        total_biaya,
        status,
    )


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def controller(mock_repo):
    return LaporanController(mock_repo)


class TestLihatRiwayatPerWaktu:
    """Menguji pengambilan riwayat reservasi berdasarkan rentang tanggal."""

    def test_ada_data_dalam_rentang(self, controller, mock_repo):
        reservasi = _buat_reservasi("r-001", "f-001", date(2026, 5, 10), StatusReservasi.LUNAS)
        mock_repo.cari_reservasi_by_date_range.return_value = [reservasi]

        hasil = controller.lihat_riwayat_per_waktu(date(2026, 5, 1), date(2026, 5, 31))

        assert len(hasil) == 1
        assert hasil[0].id_reservasi == "r-001"
        mock_repo.cari_reservasi_by_date_range.assert_called_once_with(
            date(2026, 5, 1), date(2026, 5, 31)
        )

    def test_kosong_jika_tidak_ada_data(self, controller, mock_repo):
        mock_repo.cari_reservasi_by_date_range.return_value = []

        hasil = controller.lihat_riwayat_per_waktu(date(2026, 5, 1), date(2026, 5, 31))

        assert hasil == []

    def test_range_tidak_valid_tanggal_selesai_lebih_awal(self, controller, mock_repo):
        hasil = controller.lihat_riwayat_per_waktu(date(2026, 5, 31), date(2026, 5, 1))

        assert hasil == []
        mock_repo.cari_reservasi_by_date_range.assert_not_called()

    def test_tanggal_sama_dianggap_valid(self, controller, mock_repo):
        reservasi = _buat_reservasi("r-002", "f-001", date(2026, 5, 10), StatusReservasi.LUNAS)
        mock_repo.cari_reservasi_by_date_range.return_value = [reservasi]

        hasil = controller.lihat_riwayat_per_waktu(date(2026, 5, 10), date(2026, 5, 10))

        assert len(hasil) == 1
        mock_repo.cari_reservasi_by_date_range.assert_called_once_with(
            date(2026, 5, 10), date(2026, 5, 10)
        )


class TestLihatRiwayatPerFasilitas:
    """Menguji pengambilan riwayat reservasi berdasarkan fasilitas."""

    def test_ada_data_untuk_fasilitas(self, controller, mock_repo):
        r1 = _buat_reservasi("r-001", "f-001", date(2026, 5, 1), StatusReservasi.LUNAS)
        r2 = _buat_reservasi("r-002", "f-001", date(2026, 5, 5), StatusReservasi.BELUM_DIBAYAR)
        mock_repo.cari_reservasi_by_fasilitas.return_value = [r1, r2]

        hasil = controller.lihat_riwayat_per_fasilitas("f-001")

        assert len(hasil) == 2
        mock_repo.cari_reservasi_by_fasilitas.assert_called_once_with("f-001")

    def test_kosong_jika_fasilitas_tidak_ada_reservasi(self, controller, mock_repo):
        mock_repo.cari_reservasi_by_fasilitas.return_value = []

        hasil = controller.lihat_riwayat_per_fasilitas("f-999")

        assert hasil == []


class TestHitungTotalPendapatan:
    """Menguji perhitungan total pendapatan dari daftar reservasi."""

    def test_hanya_lunas_yang_dihitung(self, controller):
        lunas = _buat_reservasi("r-001", "f-001", date(2026, 5, 1), StatusReservasi.LUNAS, Decimal("200000"))
        belum = _buat_reservasi("r-002", "f-001", date(2026, 5, 2), StatusReservasi.BELUM_DIBAYAR, Decimal("150000"))

        total = controller.hitung_total_pendapatan([lunas, belum])

        assert total == Decimal("200000")

    def test_semua_belum_dibayar_menghasilkan_nol(self, controller):
        r1 = _buat_reservasi("r-001", "f-001", date(2026, 5, 1), StatusReservasi.BELUM_DIBAYAR, Decimal("100000"))
        r2 = _buat_reservasi("r-002", "f-001", date(2026, 5, 2), StatusReservasi.BELUM_DIBAYAR, Decimal("200000"))

        total = controller.hitung_total_pendapatan([r1, r2])

        assert total == Decimal("0")

    def test_list_kosong_menghasilkan_nol(self, controller):
        total = controller.hitung_total_pendapatan([])

        assert total == Decimal("0")

    def test_semua_lunas_dijumlahkan(self, controller):
        r1 = _buat_reservasi("r-001", "f-001", date(2026, 5, 1), StatusReservasi.LUNAS, Decimal("100000"))
        r2 = _buat_reservasi("r-002", "f-001", date(2026, 5, 2), StatusReservasi.LUNAS, Decimal("250000"))
        r3 = _buat_reservasi("r-003", "f-002", date(2026, 5, 3), StatusReservasi.LUNAS, Decimal("75000"))

        total = controller.hitung_total_pendapatan([r1, r2, r3])

        assert total == Decimal("425000")

    def test_hasil_bertipe_decimal(self, controller):
        r = _buat_reservasi("r-001", "f-001", date(2026, 5, 1), StatusReservasi.LUNAS, Decimal("100000"))

        total = controller.hitung_total_pendapatan([r])

        assert isinstance(total, Decimal)
