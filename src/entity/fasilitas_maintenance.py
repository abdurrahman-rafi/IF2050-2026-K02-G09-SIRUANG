from __future__ import annotations
from datetime import date


class FasilitasMaintenance:
    """Entity model yang merepresentasikan jadwal maintenance sebuah fasilitas."""

    def __init__(
        self,
        id_maintenance: str,
        id_fasilitas: str,
        tanggal_mulai: date,
        tanggal_selesai: date,
        keterangan: str = "",
    ) -> None:
        self._id_maintenance: str = id_maintenance
        self._id_fasilitas: str = id_fasilitas
        self._tanggal_mulai: date = tanggal_mulai
        self._tanggal_selesai: date = tanggal_selesai
        self._keterangan: str = keterangan

    @property
    def id_maintenance(self) -> str:
        return self._id_maintenance

    @property
    def id_fasilitas(self) -> str:
        return self._id_fasilitas

    @property
    def tanggal_mulai(self) -> date:
        return self._tanggal_mulai

    @property
    def tanggal_selesai(self) -> date:
        return self._tanggal_selesai

    @property
    def keterangan(self) -> str:
        return self._keterangan

    def __repr__(self) -> str:
        return (
            f"FasilitasMaintenance(id={self._id_maintenance!r}, "
            f"fasilitas={self._id_fasilitas!r}, "
            f"{self._tanggal_mulai}–{self._tanggal_selesai})"
        )
