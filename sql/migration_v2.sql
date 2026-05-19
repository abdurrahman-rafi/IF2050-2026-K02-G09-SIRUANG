-- Migrasi v2: jalankan terhadap database PostgreSQL yang sudah ada sebelum menjalankan app versi baru.

-- Bug 2: izinkan penghapusan warga yang semua reservasinya sudah LUNAS
-- id_warga di tabel reservasi menjadi nullable; FK menggunakan ON DELETE SET NULL
ALTER TABLE reservasi ALTER COLUMN id_warga DROP NOT NULL;
ALTER TABLE reservasi DROP CONSTRAINT IF EXISTS fk_reservasi_warga;
ALTER TABLE reservasi ADD CONSTRAINT fk_reservasi_warga
    FOREIGN KEY (id_warga) REFERENCES warga(id_warga) ON DELETE SET NULL;

-- Bug 4: tabel jadwal maintenance fasilitas
CREATE TABLE IF NOT EXISTS fasilitas_maintenance (
    id_maintenance  VARCHAR(36) PRIMARY KEY,
    id_fasilitas    VARCHAR(36) NOT NULL,
    tanggal_mulai   DATE        NOT NULL,
    tanggal_selesai DATE        NOT NULL,
    keterangan      TEXT        DEFAULT '',
    CONSTRAINT fk_maintenance_fasilitas
        FOREIGN KEY (id_fasilitas) REFERENCES fasilitas(id_fasilitas) ON DELETE CASCADE,
    CONSTRAINT chk_maintenance_dates CHECK (tanggal_selesai >= tanggal_mulai)
);
