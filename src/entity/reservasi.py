from __future__ import annotations
from datetime import date, time
from decimal import Decimal

from src.entity.enums import StatusReservasi


class Reservasi:
    """Entity model yang merepresentasikan data reservasi fasilitas oleh warga."""

    def __init__(
        self,
        id_reservasi: str,
        id_warga: str,
        id_fasilitas: str,
        tanggal_dibuat: date,
        jam_mulai: time,
        jam_selesai: time,
        total_biaya: Decimal,
        status: StatusReservasi,
    ) -> None:
        self._id_reservasi: str = id_reservasi
        self._id_warga: str = id_warga
        self._id_fasilitas: str = id_fasilitas
        self._tanggal_dibuat: date = tanggal_dibuat
        self._jam_mulai: time = jam_mulai
        self._jam_selesai: time = jam_selesai
        self._total_biaya: Decimal = total_biaya
        self.status: StatusReservasi = status

    # TODO
    def buat_reservasi(
        self,
        id_warga: str,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
    ) -> bool:
        """Mengisi atribut reservasi dari input dan menetapkan status awal BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga yang melakukan reservasi.
            id_fasilitas: ID fasilitas yang dipesan.
            tanggal: Tanggal reservasi.
            jam_mulai: Jam mulai penggunaan fasilitas.
            jam_selesai: Jam selesai penggunaan fasilitas.

        Returns:
            True jika reservasi berhasil dibuat.
        """
        pass

    # TODO
    def hitung_total_biaya(self, id_fasilitas: str, jam_mulai: time, jam_selesai: time) -> Decimal:
        """Menghitung total biaya reservasi: durasi_jam × harga_per_jam.

        Parameter:
            id_fasilitas: ID fasilitas untuk mendapatkan harga per jam.
            jam_mulai: Jam mulai penggunaan.
            jam_selesai: Jam selesai penggunaan.

        Returns:
            Total biaya dalam Decimal (Rupiah).
        """
        pass

    # TODO
    def pembaruan_status_pembayaran(self) -> bool:
        """Memperbarui status pembayaran reservasi dari BELUM_DIBAYAR menjadi LUNAS.

        Returns:
            True jika status berhasil diperbarui, False jika sudah LUNAS sebelumnya.
        """
        pass

    # TODO
    def lihat_detail_reservasi(self, id_reservasi: str) -> Reservasi:
        """Mengembalikan objek reservasi berdasarkan ID yang diberikan.

        Parameter:
            id_reservasi: ID reservasi yang ingin dilihat detailnya.

        Returns:
            Objek Reservasi itu sendiri.
        """
        pass

    # TODO
    def ubah_data(
        self,
        id_warga: str,
        id_fasilitas: str,
        tanggal: date,
        jam_mulai: time,
        jam_selesai: time,
    ) -> bool:
        """Mengubah data jadwal reservasi. Hanya boleh dilakukan jika status BELUM_DIBAYAR.

        Parameter:
            id_warga: ID warga (dapat diubah jika perlu).
            id_fasilitas: ID fasilitas yang dipesan.
            tanggal: Tanggal baru reservasi.
            jam_mulai: Jam mulai baru.
            jam_selesai: Jam selesai baru.

        Returns:
            True jika perubahan berhasil, False jika status sudah LUNAS atau data tidak valid.
        """
        pass

    @property
    def id_reservasi(self) -> str:
        return self._id_reservasi

    @property
    def id_warga(self) -> str:
        return self._id_warga

    @property
    def id_fasilitas(self) -> str:
        return self._id_fasilitas

    @property
    def tanggal_dibuat(self) -> date:
        return self._tanggal_dibuat

    @property
    def jam_mulai(self) -> time:
        return self._jam_mulai

    @property
    def jam_selesai(self) -> time:
        return self._jam_selesai

    @property
    def total_biaya(self) -> Decimal:
        return self._total_biaya
