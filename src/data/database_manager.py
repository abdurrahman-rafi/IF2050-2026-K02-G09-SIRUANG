from __future__ import annotations
from typing import Any, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    """Mengelola koneksi ke database, eksekusi query parameterized, dan backup data lokal."""

    def __init__(self, url_database: str) -> None:
        self._koneksi: Optional[Any] = None
        self._url_database: str = url_database

    def _resolusi_url(self) -> str:
        """Menentukan URL koneksi dari atribut, env var, atau config.ini."""
        if self._url_database:
            return self._url_database
        url_env = os.environ.get("SIRUANG_DB_URL", "")
        if url_env:
            return url_env
        config_path = Path(__file__).parents[2] / "config.ini"
        if config_path.exists():
            cfg = configparser.ConfigParser()
            cfg.read(config_path)
            return cfg.get("database", "url", fallback="")
        return ""

    def buka_koneksi(self) -> bool:
        """Membuka koneksi ke database menggunakan url_database yang dikonfigurasi.

        Returns:
            True jika koneksi berhasil dibuka, False jika gagal.
        """
        try:
            url = self._resolusi_url()
            self._koneksi = psycopg2.connect(url)
            return True
        except Exception as e:
            print(f"[DatabaseManager] Gagal membuka koneksi: {e}", flush=True)
            return False

    def tutup_koneksi(self) -> None:
        """Menutup koneksi ke database setelah semua operasi selesai."""
        try:
            if self._koneksi and not self._koneksi.closed:
                self._koneksi.close()
        except Exception as e:
            print(f"[DatabaseManager] Gagal menutup koneksi: {e}", flush=True)

    def simpan_data(self, query: str, params: tuple = ()) -> bool:
        """Mengeksekusi query INSERT atau UPDATE dengan parameter parameterized.

        Parameter:
            query: Query SQL parameterized (gunakan placeholder ? atau %s).
            params: Tuple nilai parameter yang menggantikan placeholder pada query.

        Returns:
            True jika query berhasil dieksekusi, False jika terjadi error.
        """
        pass

    # TODO
    def ambil_data(self, query: str, params: tuple = ()) -> List[Any]:
        """Mengeksekusi query SELECT dan mengembalikan hasil sebagai list.

        Parameter:
            query: Query SQL SELECT parameterized.
            params: Tuple nilai parameter yang menggantikan placeholder pada query.

        Returns:
            List berisi baris hasil query, atau list kosong jika tidak ada data.
        """
        pass

    # TODO
    def hapus_data(self, query: str, params: tuple = ()) -> bool:
        """Mengeksekusi query DELETE untuk menghapus data dari database.

        Parameter:
            query: Query SQL DELETE parameterized.
            params: Tuple nilai parameter yang menggantikan placeholder pada query.

        Returns:
            True jika penghapusan berhasil, False jika terjadi error.
        """
        pass

    # TODO
    def backup_data(self) -> bool:
        """Menyimpan salinan seluruh data ke file SQL lokal di direktori backup/.
        Nama file berdasarkan timestamp saat backup dilakukan.

        Returns:
            True jika backup berhasil, False jika terjadi error.
        """
        pass
