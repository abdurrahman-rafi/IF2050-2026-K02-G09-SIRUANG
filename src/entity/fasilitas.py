from __future__ import annotations
from decimal import Decimal
from src.entity.enums import StatusFasilitas

class Fasilitas:
    """Entity model yang merepresentasikan data fasilitas komunitas yang dapat direservasi."""

    def __init__(
        self,
        id_fasilitas: str,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> None:
        self._id_fasilitas: str = id_fasilitas
        self._nama: str = nama
        self._harga_per_jam: Decimal = harga_per_jam
        self._deskripsi: str = deskripsi
        self._status: StatusFasilitas = status

    def ubah_data(
        self,
        nama: str,
        harga_per_jam: Decimal,
        deskripsi: str,
        status: StatusFasilitas,
    ) -> bool:
        """Memperbarui atribut fasilitas berdasarkan input baru dari controller."""
        self._nama = nama
        self._harga_per_jam = harga_per_jam
        self._deskripsi = deskripsi
        self._status = status
        return True

    def get_detail_fasilitas(self) -> Fasilitas:
        """Mengembalikan objek fasilitas ini beserta seluruh atributnya."""
        return self

    @property
    def id_fasilitas(self) -> str:
        return self._id_fasilitas

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def harga_per_jam(self) -> Decimal:
        return self._harga_per_jam

    @property
    def deskripsi(self) -> str:
        return self._deskripsi

    @property
    def status(self) -> StatusFasilitas:
        return self._status