import pytest
from unittest.mock import MagicMock, patch

from src.data.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test suite untuk DatabaseManager."""

    def _buat_db(self) -> DatabaseManager:
        return DatabaseManager("postgresql://user:pass@localhost/siruang")

    def _buat_mock_koneksi(self, db: DatabaseManager):
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        db._koneksi = mock_conn
        return mock_conn, mock_cursor

    def test_buka_koneksi_berhasil(self):
        """Menguji buka_koneksi mengembalikan True dan menyimpan koneksi."""
        db = self._buat_db()
        mock_conn = MagicMock()
        with patch("psycopg2.connect", return_value=mock_conn):
            result = db.buka_koneksi()
        assert result is True
        assert db._koneksi is mock_conn

    def test_buka_koneksi_gagal(self):
        """Menguji buka_koneksi mengembalikan False jika psycopg2 melempar exception."""
        db = self._buat_db()
        with patch("psycopg2.connect", side_effect=Exception("koneksi ditolak")):
            result = db.buka_koneksi()
        assert result is False

    def test_buka_koneksi_gunakan_env_var(self, monkeypatch):
        """Menguji buka_koneksi menggunakan env var SIRUANG_DB_URL jika url_database kosong."""
        db = DatabaseManager("")
        url_env = "postgresql://env_user:pass@localhost/siruang"
        monkeypatch.setenv("SIRUANG_DB_URL", url_env)
        with patch("psycopg2.connect", return_value=MagicMock()) as mock_connect:
            db.buka_koneksi()
        mock_connect.assert_called_once_with(url_env)

    def test_tutup_koneksi(self):
        """Menguji tutup_koneksi memanggil close() pada koneksi yang terbuka."""
        db = self._buat_db()
        mock_conn = MagicMock()
        mock_conn.closed = False
        db._koneksi = mock_conn
        db.tutup_koneksi()
        mock_conn.close.assert_called_once()

    def test_tutup_koneksi_sudah_tertutup(self):
        """Menguji tutup_koneksi tidak memanggil close() jika koneksi sudah tertutup."""
        db = self._buat_db()
        mock_conn = MagicMock()
        mock_conn.closed = True
        db._koneksi = mock_conn
        db.tutup_koneksi()
        mock_conn.close.assert_not_called()

    def test_simpan_data_berhasil(self):
        """Menguji simpan_data mengeksekusi query, commit, dan mengembalikan True."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        result = db.simpan_data(
            "INSERT INTO warga VALUES (%s, %s, %s, %s)",
            ("id-1", "Andi", "Jl. A", "081"),
        )
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_simpan_data_gagal_rollback(self):
        """Menguji simpan_data melakukan rollback dan mengembalikan False jika terjadi error."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        mock_cursor.execute.side_effect = Exception("constraint violation")
        result = db.simpan_data("INSERT INTO warga VALUES (%s)", ("id-1",))
        assert result is False
        mock_conn.rollback.assert_called_once()

    def test_ambil_data_berhasil(self):
        """Menguji ambil_data mengembalikan list dict hasil query SELECT."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        mock_cursor.fetchall.return_value = [
            {"id_warga": "id-1", "nama": "Andi", "alamat": "Jl. A", "no_hp": "081"}
        ]
        result = db.ambil_data("SELECT * FROM warga", ())
        assert len(result) == 1
        assert result[0]["nama"] == "Andi"

    def test_ambil_data_gagal_kembalikan_list_kosong(self):
        """Menguji ambil_data mengembalikan list kosong jika terjadi error query."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        mock_cursor.execute.side_effect = Exception("tabel tidak ditemukan")
        result = db.ambil_data("SELECT * FROM warga", ())
        assert result == []

    def test_hapus_data_berhasil(self):
        """Menguji hapus_data mengeksekusi DELETE, commit, dan mengembalikan True."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        result = db.hapus_data("DELETE FROM warga WHERE id_warga=%s", ("id-1",))
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM warga WHERE id_warga=%s", ("id-1",)
        )
        mock_conn.commit.assert_called_once()

    def test_hapus_data_gagal_rollback(self):
        """Menguji hapus_data melakukan rollback dan mengembalikan False jika terjadi error."""
        db = self._buat_db()
        mock_conn, mock_cursor = self._buat_mock_koneksi(db)
        mock_cursor.execute.side_effect = Exception("foreign key constraint")
        result = db.hapus_data("DELETE FROM warga WHERE id_warga=%s", ("id-1",))
        assert result is False
        mock_conn.rollback.assert_called_once()

    def test_backup_data_berhasil(self):
        """Menguji backup_data membuat direktori backup, menulis file SQL, dan mengembalikan True."""
        db = self._buat_db()
        db._koneksi = MagicMock()
        db.ambil_data = MagicMock(return_value=[])

        with patch("src.data.database_manager.Path") as MockPath:
            mock_root = MagicMock()
            mock_backup_dir = MagicMock()
            mock_backup_file = MagicMock()
            MockPath.return_value.parents.__getitem__.return_value = mock_root
            mock_root.__truediv__ = MagicMock(return_value=mock_backup_dir)
            mock_backup_dir.__truediv__ = MagicMock(return_value=mock_backup_file)

            result = db.backup_data()

        assert result is True
        mock_backup_dir.mkdir.assert_called_once_with(exist_ok=True)
        mock_backup_file.write_text.assert_called_once()

    def test_backup_data_gagal(self):
        """Menguji backup_data mengembalikan False jika terjadi error saat proses backup."""
        db = self._buat_db()
        db._koneksi = MagicMock()

        with patch("src.data.database_manager.Path") as MockPath:
            mock_dir = MagicMock()
            mock_dir.mkdir.side_effect = Exception("disk penuh")
            MockPath.return_value.parents.__getitem__.return_value.__truediv__.return_value = mock_dir

            result = db.backup_data()

        assert result is False
