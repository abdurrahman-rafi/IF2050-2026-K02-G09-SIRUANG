from __future__ import annotations
from datetime import datetime
from typing import Optional

class Notifikasi:
    """Entity model yang merepresentasikan data notifikasi in-app untuk pengelola."""

    def __init__(
        self,
        id_notifikasi: str,
        id_reservasi: str,
        pesan_notifikasi: str,
        waktu_kirim: Optional[datetime] = None,
        sudah_dibaca: bool = False,
    ) -> None:
        """
        Constructor.

        Args:
            id_notifikasi: ID unik notifikasi.
            id_reservasi: ID reservasi terkait.
            pesan_notifikasi: Isi pesan notifikasi.
            waktu_kirim: Waktu pengiriman; jika None akan di-set ke waktu sekarang.
            sudah_dibaca: Status apakah notifikasi sudah dibaca (default False).
        """
        self._id_notifikasi: str = id_notifikasi
        self._id_reservasi: str = id_reservasi
        self._pesan_notifikasi: str = pesan_notifikasi
        self._waktu_kirim: datetime = waktu_kirim if waktu_kirim is not None else datetime.now()
        self._sudah_dibaca: bool = sudah_dibaca

    def get_detail_notifikasi(self) -> "Notifikasi":
        """Mengembalikan objek Notifikasi ini beserta seluruh detail atributnya."""
        return self

    def create_notifikasi(self) -> None:
        """Inisialisasi nilai awal untuk entitas notifikasi baru:
        menetapkan waktu_kirim ke waktu sekarang dan sudah_dibaca ke False.
        """
        self._waktu_kirim = datetime.now()
        self._sudah_dibaca = False

    def tandai_sudah_dibaca(self) -> None:
        """Ubah status sudah_dibaca jadi True."""
        self._sudah_dibaca = True

    @property
    def id_notifikasi(self) -> str:
        return self._id_notifikasi

    @property
    def id_reservasi(self) -> str:
        return self._id_reservasi

    @property
    def pesan_notifikasi(self) -> str:
        return self._pesan_notifikasi

    @property
    def waktu_kirim(self) -> datetime:
        return self._waktu_kirim

    @property
    def sudah_dibaca(self) -> bool:
        return self._sudah_dibaca

    @sudah_dibaca.setter
    def sudah_dibaca(self, value: bool) -> None:
        self._sudah_dibaca = bool(value)

    def __repr__(self) -> str:
        return (
            f"Notifikasi(id_notifikasi={self._id_notifikasi!r}, "
            f"id_reservasi={self._id_reservasi!r}, "
            f"waktu_kirim={self._waktu_kirim.isoformat()}, "
            f"sudah_dibaca={self._sudah_dibaca})"
        )
