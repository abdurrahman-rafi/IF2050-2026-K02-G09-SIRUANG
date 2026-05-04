from __future__ import annotations
from datetime import datetime


class Notifikasi:
    """Entity model yang merepresentasikan data notifikasi in-app untuk pengelola."""

    def __init__(
        self,
        id_notifikasi: str,
        id_reservasi: str,
        pesan_notifikasi: str,
        waktu_kirim: datetime,
        sudah_dibaca: bool,
    ) -> None:
        self._id_notifikasi: str = id_notifikasi
        self._id_reservasi: str = id_reservasi
        self._pesan_notifikasi: str = pesan_notifikasi
        self._waktu_kirim: datetime = waktu_kirim
        self._sudah_dibaca: bool = sudah_dibaca

    # TODO
    def get_detail_notifikasi(self) -> Notifikasi:
        """Mengembalikan objek notifikasi ini beserta seluruh detail atributnya.

        Returns:
            Objek Notifikasi itu sendiri.
        """
        pass

    # TODO
    def create_notifikasi(self) -> None:
        """Menginisiasi nilai awal untuk entitas notifikasi baru:
        menetapkan waktu_kirim ke waktu sekarang dan sudah_dibaca ke False.
        """
        pass

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
