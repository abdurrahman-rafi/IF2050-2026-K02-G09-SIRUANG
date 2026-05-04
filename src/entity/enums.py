from enum import Enum


class StatusFasilitas(Enum):
    READY_TO_BOOK = "READY_TO_BOOK"
    MAINTENANCE = "MAINTENANCE"


class StatusReservasi(Enum):
    BELUM_DIBAYAR = "BELUM_DIBAYAR"
    LUNAS = "LUNAS"
