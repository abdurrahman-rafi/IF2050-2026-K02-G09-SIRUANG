# SIRUANG — Sistem Reservasi Fasilitas

Aplikasi desktop untuk pengelolaan reservasi fasilitas komunitas. Berjalan secara lokal (localhost) tanpa koneksi internet.

## Tech Stack

- **Bahasa:** Python 3.10+
- **UI Framework:** PyQt6
- **Database:** MySQL 8.0+ 
- **Arsitektur:** ECB (Entity-Control-Boundary) - Layered Architecture

## Struktur Proyek

```
SIRUANG/
├── src/
│   ├── main.py                        # Entry point aplikasi
│   ├── entity/                        # Entity model (Warga, Fasilitas, Reservasi, Notifikasi)
│   ├── controller/                    # Business logic (WargaController, FasilitasController, ...)
│   ├── view/                          # Tampilan PyQt6 (WargaView, FasilitasView, ...)
│   ├── data/                          # DatabaseManager + DataRepository
│   └── service/                       # NotificationService
├── tests/                             # Unit test dengan pytest
├── sql/
│   └── schema.sql                     # DDL tabel database
├── doc/                               # Screenshot dan dokumentasi
├── img/                               # Aset gambar aplikasi
├── requirements.txt
└── README.md
```

## Fitur Utama

| Use Case | Fitur |
|----------|-------|
| UC01-UC04 | Manajemen data warga (CRUD) |
| UC05-UC08 | Manajemen data fasilitas (CRUD + status) |
| UC09-UC11 | Pencatatan reservasi, validasi jadwal, update status pembayaran |
| UC12-UC13 | Laporan riwayat transaksi per waktu dan per fasilitas |
| UC14 | Notifikasi in-app reservasi yang akan segera berakhir |

## Aturan Bisnis

- Warga/Fasilitas tidak dapat dihapus jika masih memiliki reservasi berstatus `BELUM_DIBAYAR`
- Reservasi berstatus `LUNAS` tidak dapat diubah waktunya atau dihapus
- Validasi jadwal: tidak boleh ada overlap pada fasilitas dan tanggal yang sama
- Total biaya: `durasi_jam × harga_per_jam`
- Laporan pendapatan hanya menghitung reservasi berstatus `LUNAS`
