-- Schema basis data SIRUANG (Sistem Reservasi Fasilitas)
-- Kompatibel dengan MySQL 8.0+ dan PostgreSQL 14+

CREATE TABLE IF NOT EXISTS warga (
    id_warga    VARCHAR(36)  PRIMARY KEY,
    nama        VARCHAR(100) NOT NULL,
    alamat      VARCHAR(255) NOT NULL,
    no_hp       VARCHAR(20)  NOT NULL
);

CREATE TABLE IF NOT EXISTS fasilitas (
    id_fasilitas  VARCHAR(36)    PRIMARY KEY,
    nama          VARCHAR(100)   NOT NULL,
    harga_per_jam DECIMAL(12, 2) NOT NULL,
    deskripsi     TEXT,
    status        VARCHAR(20)    NOT NULL DEFAULT 'READY_TO_BOOK',
    -- status: 'READY_TO_BOOK' | 'MAINTENANCE'
    CONSTRAINT chk_status_fasilitas CHECK (status IN ('READY_TO_BOOK', 'MAINTENANCE'))
);

CREATE TABLE IF NOT EXISTS reservasi (
    id_reservasi  VARCHAR(36)    PRIMARY KEY,
    id_warga      VARCHAR(36)    NOT NULL,
    id_fasilitas  VARCHAR(36)    NOT NULL,
    tanggal_dibuat DATE          NOT NULL,
    jam_mulai     TIME           NOT NULL,
    jam_selesai   TIME           NOT NULL,
    total_biaya   DECIMAL(12, 2) NOT NULL,
    status        VARCHAR(20)    NOT NULL DEFAULT 'BELUM_DIBAYAR',
    -- status: 'BELUM_DIBAYAR' | 'LUNAS'
    CONSTRAINT chk_status_reservasi CHECK (status IN ('BELUM_DIBAYAR', 'LUNAS')),
    CONSTRAINT chk_jam CHECK (jam_selesai > jam_mulai),
    CONSTRAINT fk_reservasi_warga     FOREIGN KEY (id_warga)    REFERENCES warga(id_warga),
    CONSTRAINT fk_reservasi_fasilitas FOREIGN KEY (id_fasilitas) REFERENCES fasilitas(id_fasilitas)
);

CREATE TABLE IF NOT EXISTS notifikasi (
    id_notifikasi    VARCHAR(36) PRIMARY KEY,
    id_reservasi     VARCHAR(36) NOT NULL,
    pesan_notifikasi TEXT        NOT NULL,
    waktu_kirim      TIMESTAMP   NOT NULL,
    sudah_dibaca     BOOLEAN     NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_notifikasi_reservasi FOREIGN KEY (id_reservasi) REFERENCES reservasi(id_reservasi)
);

-- Index untuk mempercepat query validasi jadwal (Q-002)
CREATE INDEX IF NOT EXISTS idx_reservasi_fasilitas_tanggal
    ON reservasi (id_fasilitas, tanggal_dibuat);

-- Index untuk mempercepat query laporan (Q-003, Q-004)
CREATE INDEX IF NOT EXISTS idx_reservasi_tanggal
    ON reservasi (tanggal_dibuat);
