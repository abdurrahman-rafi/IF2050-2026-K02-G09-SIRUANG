"""Seed PostgreSQL database from static/baseseed.db (SQLite).

Usage: python seed.py
"""
import sqlite3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg2

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/siruang"

STATUS_FASILITAS_MAP = {
    "TERSEDIA": "READY_TO_BOOK",
    "TIDAK_TERSEDIA": "MAINTENANCE",
    "READY_TO_BOOK": "READY_TO_BOOK",
    "MAINTENANCE": "MAINTENANCE",
}

GAMBAR_MAP = [
    ("Aula", "aula.jpg"),
    ("Badminton", "badminton.jpg"),
    ("Kolam", "kolam.jpg"),
]


def _gambar_untuk(nama: str) -> str:
    for keyword, filename in GAMBAR_MAP:
        if keyword.lower() in nama.lower():
            return filename
    return ""


def seed() -> None:
    sqlite_conn = sqlite3.connect("static/baseseed.db")
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(DATABASE_URL)
    pg = pg_conn.cursor()

    try:
        pg.execute("TRUNCATE warga, fasilitas, reservasi, notifikasi CASCADE")
        print("  Tabel dikosongkan.")

        pg.execute("ALTER TABLE fasilitas ADD COLUMN IF NOT EXISTS gambar TEXT DEFAULT ''")
        print("  Kolom gambar siap.")

        # Warga
        warga_rows = cur.execute("SELECT * FROM warga").fetchall()
        for r in warga_rows:
            pg.execute(
                "INSERT INTO warga (id_warga, nama, alamat, no_hp) VALUES (%s, %s, %s, %s)",
                (r["id_warga"], r["nama"], r["alamat"], r["no_hp"]),
            )
        print(f"  Warga: {len(warga_rows)} baris.")

        # Fasilitas
        fasilitas_rows = cur.execute("SELECT * FROM fasilitas").fetchall()
        for r in fasilitas_rows:
            status = STATUS_FASILITAS_MAP.get(r["status"], "READY_TO_BOOK")
            gambar = _gambar_untuk(r["nama"])
            pg.execute(
                "INSERT INTO fasilitas "
                "(id_fasilitas, nama, harga_per_jam, deskripsi, status, gambar) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (r["id_fasilitas"], r["nama"], r["harga_per_jam"],
                 r["deskripsi"], status, gambar),
            )
        print(f"  Fasilitas: {len(fasilitas_rows)} baris.")

        # Reservasi (SQLite: tanggal → PostgreSQL: tanggal_dibuat)
        reservasi_rows = cur.execute("SELECT * FROM reservasi").fetchall()
        seeded_reservasi_ids: set = set()
        for r in reservasi_rows:
            pg.execute(
                "INSERT INTO reservasi "
                "(id_reservasi, id_warga, id_fasilitas, tanggal_dibuat, "
                "jam_mulai, jam_selesai, total_biaya, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    r["id_reservasi"], r["id_warga"], r["id_fasilitas"],
                    r["tanggal"], r["jam_mulai"], r["jam_selesai"],
                    r["total_biaya"], r["status"],
                ),
            )
            seeded_reservasi_ids.add(r["id_reservasi"])
        print(f"  Reservasi: {len(reservasi_rows)} baris.")

        # Reservasi sintetis untuk uji notifikasi (berakhir ~20 menit dari sekarang)
        now = datetime.now()
        jam_mulai = (now - timedelta(minutes=90)).time()
        jam_selesai = (now + timedelta(minutes=20)).time()
        total_biaya = float(Decimal("50000") * Decimal(str(110 / 60)))
        id_near = str(uuid.uuid4())
        id_warga_budi = next(r["id_warga"] for r in warga_rows if "Budi" in r["nama"])
        id_fasilitas_aula = next(
            r["id_fasilitas"] for r in fasilitas_rows if "Aula" in r["nama"]
        )
        pg.execute(
            "INSERT INTO reservasi "
            "(id_reservasi, id_warga, id_fasilitas, tanggal_dibuat, "
            "jam_mulai, jam_selesai, total_biaya, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                id_near, id_warga_budi, id_fasilitas_aula,
                now.date(), jam_mulai, jam_selesai,
                round(total_biaya, 2), "BELUM_DIBAYAR",
            ),
        )
        seeded_reservasi_ids.add(id_near)
        print(
            f"  Reservasi near-expiry: jam_selesai="
            f"{jam_selesai.strftime('%H:%M')} (~20 menit dari sekarang)."
        )

        # Notifikasi (SQLite: pesan → PostgreSQL: pesan_notifikasi)
        notifikasi_rows = cur.execute("SELECT * FROM notifikasi").fetchall()
        seeded_n = 0
        for r in notifikasi_rows:
            if r["id_reservasi"] not in seeded_reservasi_ids:
                continue
            pg.execute(
                "INSERT INTO notifikasi "
                "(id_notifikasi, id_reservasi, pesan_notifikasi, waktu_kirim, sudah_dibaca) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    r["id_notifikasi"], r["id_reservasi"], r["pesan"],
                    r["waktu_kirim"], bool(r["sudah_dibaca"]),
                ),
            )
            seeded_n += 1
        print(f"  Notifikasi: {seeded_n} baris.")

        pg_conn.commit()
        print("\nSeed berhasil.")

    except Exception as exc:
        pg_conn.rollback()
        print(f"Error: {exc}")
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    seed()
