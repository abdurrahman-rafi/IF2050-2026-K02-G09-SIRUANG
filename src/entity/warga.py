from __future__ import annotations


class Warga:
    """Entity model yang merepresentasikan data warga terdaftar dalam sistem."""

    def __init__(self, id_warga: str, nama: str, alamat: str, no_hp: str) -> None:
        self._id_warga: str = id_warga
        self._nama: str = nama
        self._alamat: str = alamat
        self._no_hp: str = no_hp

    # TODO
    def validate_data(self) -> bool:
        """Memvalidasi kelengkapan dan format data warga: nama tidak boleh kosong,
        alamat tidak boleh kosong, no_hp hanya boleh berisi angka dan tidak boleh kosong.

        Returns:
            True jika semua data valid, False jika ada data yang tidak valid.
        """
        pass

    # TODO
    def ubah_data(self, nama: str, alamat: str, no_hp: str) -> None:
        """Memperbarui atribut nama, alamat, dan no_hp warga dengan nilai baru.

        Parameter:
            nama: Nama baru warga.
            alamat: Alamat baru warga.
            no_hp: Nomor HP baru warga.
        """
        pass

    @property
    def id_warga(self) -> str:
        return self._id_warga

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def alamat(self) -> str:
        return self._alamat

    @property
    def no_hp(self) -> str:
        return self._no_hp
