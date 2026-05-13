# SIRUANG — Sistem Reservasi Fasilitas

Aplikasi desktop untuk pengelolaan reservasi fasilitas komunitas. Berjalan secara lokal (localhost) tanpa koneksi internet.

## Tech Stack

- **Bahasa:** Python 3.10+
- **UI Framework:** PyQt6
- **Database:** PostgreSQL 14+
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

## Cara Run

### Requirement

- Python 3.10+
- PostgreSQL 14+

### 1. Clone dan ke direktori

```bash
git clone <url-repo>
cd SIRUANG
```

### 2. Buat virtual environment dan install dependency

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Buat database PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE siruang;"
psql -U postgres -d siruang -f sql/schema.sql
```

### 4. Konfigurasi koneksi database

Edit baris `DATABASE_URL` di `src/main.py` sesuai kredensial PostgreSQL kamu:

```python
DATABASE_URL = "postgresql://<user>:<password>@localhost:5432/siruang"
```

Atau set environment variable sebelum menjalankan:

```bash
export SIRUANG_DB_URL="postgresql://<user>:<password>@localhost:5432/siruang"
```

Atau buat file `config.ini` di root proyek:

```ini
[database]
url = postgresql://<user>:<password>@localhost:5432/siruang
```

### 5. Jalankan aplikasi

```bash
python -m src.main
```

### 6. (Opsional) Jalankan seed data

```bash
python seed.py
```

### 7. (Opsional) Jalankan test

```bash
pytest tests/
```

---

## Aturan Bisnis

- Warga/Fasilitas tidak dapat dihapus jika masih memiliki reservasi berstatus `BELUM_DIBAYAR`
- Reservasi berstatus `LUNAS` tidak dapat diubah waktunya atau dihapus
- Validasi jadwal: tidak boleh ada overlap pada fasilitas dan tanggal yang sama
- Total biaya: `durasi_jam × harga_per_jam`
- Laporan pendapatan hanya menghitung reservasi berstatus `LUNAS`
