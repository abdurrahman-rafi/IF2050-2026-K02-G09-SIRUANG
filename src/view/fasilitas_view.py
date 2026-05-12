from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.controller.fasilitas_controller import FasilitasController
from src.entity.enums import StatusFasilitas

if TYPE_CHECKING:
    from src.data.data_repository import DataRepository
    from src.entity.fasilitas import Fasilitas


class FasilitasView(QWidget):
    """Tampilan pengelolaan data fasilitas: landing page, tambah, detail, edit, hapus (UC05-UC08)."""

    def __init__(
        self,
        data_repository: DataRepository,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._data_repository: DataRepository = data_repository
        self._controller = FasilitasController(data_repository)
        self._semua_fasilitas: List[Fasilitas] = []
        self._setup_ui()
        self._muat_fasilitas()

    # ------------------------------------------------------------------ #
    # Setup awal UI                                                        #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header: judul + tombol tambah
        header = QHBoxLayout()
        judul = QLabel("Manajemen Fasilitas")
        judul.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.addWidget(judul)
        header.addStretch()
        btn_tambah = QPushButton("+ Tambah Fasilitas")
        btn_tambah.setFixedHeight(36)
        btn_tambah.clicked.connect(self.tampilkan_form_tambah_fasilitas)
        header.addWidget(btn_tambah)
        layout.addLayout(header)

        # Baris pencarian dan filter status
        baris_filter = QHBoxLayout()
        self._input_cari = QLineEdit()
        self._input_cari.setPlaceholderText("Cari nama fasilitas...")
        self._input_cari.setFixedHeight(32)
        self._input_cari.textChanged.connect(self._terapkan_filter)
        baris_filter.addWidget(self._input_cari)

        self._combo_status = QComboBox()
        self._combo_status.setFixedHeight(32)
        self._combo_status.addItem("Semua Status", None)
        for s in StatusFasilitas:
            self._combo_status.addItem(s.value.replace("_", " "), s)
        self._combo_status.currentIndexChanged.connect(self._terapkan_filter)
        baris_filter.addWidget(self._combo_status)
        layout.addLayout(baris_filter)

        # Area scroll untuk grid kartu fasilitas
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(12)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    # ------------------------------------------------------------------ #
    # Metode internal                                                      #
    # ------------------------------------------------------------------ #

    def _muat_fasilitas(self) -> None:
        self._semua_fasilitas = self._controller.lihat_daftar_fasilitas()
        self.tampilkan_daftar_fasilitas(self._semua_fasilitas)

    def _terapkan_filter(self) -> None:
        kata = self._input_cari.text().strip().lower()
        filter_status: Optional[StatusFasilitas] = self._combo_status.currentData()

        hasil = [
            f for f in self._semua_fasilitas
            if (kata in f.nama.lower())
            and (filter_status is None or f.status == filter_status)
        ]
        self.tampilkan_daftar_fasilitas(hasil)

    def _bersihkan_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _buat_kartu(self, fasilitas: Fasilitas) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFixedSize(200, 130)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setToolTip("Klik untuk melihat detail")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)

        label_nama = QLabel(fasilitas.nama)
        label_nama.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        label_nama.setWordWrap(True)

        label_harga = QLabel(f"Rp {int(fasilitas.harga_per_jam):,}/jam")
        label_harga.setStyleSheet("color: #555;")

        warna = "#27ae60" if fasilitas.status == StatusFasilitas.READY_TO_BOOK else "#e67e22"
        label_status = QLabel(fasilitas.status.value.replace("_", " "))
        label_status.setStyleSheet(f"color: {warna}; font-weight: bold; font-size: 10px;")

        layout.addWidget(label_nama)
        layout.addWidget(label_harga)
        layout.addStretch()
        layout.addWidget(label_status)

        frame.mousePressEvent = lambda _event, f=fasilitas: self.tampilkan_detail_fasilitas(f)
        return frame

    # ------------------------------------------------------------------ #
    # Metode publik (sesuai kontrak dari template)                         #
    # ------------------------------------------------------------------ #

    def tampilkan_daftar_fasilitas(self, daftar_fasilitas: List[Fasilitas]) -> None:
        """Menampilkan landing page daftar fasilitas dalam format card grid."""
        self._bersihkan_grid()

        if not daftar_fasilitas:
            label = QLabel("Tidak ada fasilitas yang sesuai.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #888; font-size: 13px;")
            self._grid.addWidget(label, 0, 0)
            return

        jumlah_kolom = 4
        for i, fasilitas in enumerate(daftar_fasilitas):
            kartu = self._buat_kartu(fasilitas)
            self._grid.addWidget(kartu, i // jumlah_kolom, i % jumlah_kolom)

    def tampilkan_form_tambah_fasilitas(self) -> None:
        """Menampilkan dialog form input untuk menambahkan data fasilitas baru."""
        dialog = _FormFasilitasDialog("Tambah Fasilitas Baru", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            berhasil = self._controller.tambah_fasilitas(
                data["nama"],
                data["harga_per_jam"],
                data["deskripsi"],
                data["status"],
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Fasilitas berhasil ditambahkan.")
                self._muat_fasilitas()
            else:
                self.tampilkan_pesan_error(
                    "Gagal menambahkan fasilitas. Pastikan nama tidak kosong dan harga lebih dari 0."
                )

    def tampilkan_detail_fasilitas(self, fasilitas: Fasilitas) -> None:
        """Menampilkan halaman detail fasilitas yang dipilih."""
        dialog = _DetailFasilitasDialog(fasilitas, parent=self)
        aksi = dialog.exec()

        if dialog.aksi_dipilih == "edit":
            self.tampilkan_form_ubah_fasilitas(fasilitas)
        elif dialog.aksi_dipilih == "hapus":
            self.tampilkan_konfirmasi_hapus(fasilitas)

    def tampilkan_form_ubah_fasilitas(self, fasilitas: Fasilitas) -> None:
        """Menampilkan form edit dengan data fasilitas yang sudah ada sebagai nilai awal."""
        dialog = _FormFasilitasDialog("Edit Fasilitas", fasilitas=fasilitas, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            berhasil = self._controller.ubah_fasilitas(
                fasilitas.id_fasilitas,
                data["nama"],
                data["harga_per_jam"],
                data["deskripsi"],
                data["status"],
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Fasilitas berhasil diperbarui.")
                self._muat_fasilitas()
            else:
                self.tampilkan_pesan_error("Gagal memperbarui fasilitas. Periksa kembali data yang dimasukkan.")

    def tampilkan_konfirmasi_hapus(self, fasilitas: Fasilitas) -> None:
        """Menampilkan dialog konfirmasi sebelum proses penghapusan fasilitas dijalankan."""
        jawab = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus fasilitas '{fasilitas.nama}'?\nTindakan ini tidak dapat dibatalkan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if jawab == QMessageBox.StandardButton.Yes:
            berhasil = self._controller.hapus_fasilitas(fasilitas.id_fasilitas)
            if berhasil:
                self.tampilkan_pesan_berhasil(f"Fasilitas '{fasilitas.nama}' berhasil dihapus.")
                self._muat_fasilitas()
            else:
                self.tampilkan_pesan_error(
                    f"Fasilitas '{fasilitas.nama}' tidak dapat dihapus "
                    "karena masih memiliki reservasi aktif (belum dibayar)."
                )

    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses."""
        QMessageBox.information(self, "Berhasil", pesan)

    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error."""
        QMessageBox.critical(self, "Gagal", pesan)


# ------------------------------------------------------------------ #
# Dialog pembantu (tidak diekspos ke luar modul)                       #
# ------------------------------------------------------------------ #

class _FormFasilitasDialog(QDialog):
    """Dialog form untuk tambah dan edit fasilitas."""

    def __init__(
        self,
        judul: str,
        fasilitas: Optional[Fasilitas] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(judul)
        self.setMinimumWidth(420)
        self._setup_ui(fasilitas)

    def _setup_ui(self, fasilitas: Optional[Fasilitas]) -> None:
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self._input_nama = QLineEdit()
        self._input_nama.setPlaceholderText("Contoh: Balai Warga RW 03")

        self._input_harga = QDoubleSpinBox()
        self._input_harga.setMinimum(1)
        self._input_harga.setMaximum(99_999_999)
        self._input_harga.setDecimals(0)
        self._input_harga.setSingleStep(10_000)
        self._input_harga.setPrefix("Rp ")

        self._input_deskripsi = QTextEdit()
        self._input_deskripsi.setFixedHeight(80)
        self._input_deskripsi.setPlaceholderText("Deskripsi singkat fasilitas (opsional)")

        self._input_status = QComboBox()
        for s in StatusFasilitas:
            self._input_status.addItem(s.value.replace("_", " "), s)

        # Isi nilai awal kalau mode edit
        if fasilitas is not None:
            self._input_nama.setText(fasilitas.nama)
            self._input_harga.setValue(float(fasilitas.harga_per_jam))
            self._input_deskripsi.setPlainText(fasilitas.deskripsi or "")
            idx = self._input_status.findData(fasilitas.status)
            if idx >= 0:
                self._input_status.setCurrentIndex(idx)

        layout.addRow("Nama Fasilitas *", self._input_nama)
        layout.addRow("Harga per Jam *", self._input_harga)
        layout.addRow("Deskripsi", self._input_deskripsi)
        layout.addRow("Status", self._input_status)

        tombol = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        tombol.button(QDialogButtonBox.StandardButton.Ok).setText("Simpan")
        tombol.accepted.connect(self.accept)
        tombol.rejected.connect(self.reject)
        layout.addRow(tombol)

    def get_data(self) -> dict:
        return {
            "nama": self._input_nama.text().strip(),
            "harga_per_jam": Decimal(str(int(self._input_harga.value()))),
            "deskripsi": self._input_deskripsi.toPlainText().strip(),
            "status": self._input_status.currentData(),
        }


class _DetailFasilitasDialog(QDialog):
    """Dialog yang menampilkan detail fasilitas beserta tombol aksi."""

    def __init__(self, fasilitas: Fasilitas, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._fasilitas = fasilitas
        self.aksi_dipilih: Optional[str] = None
        self.setWindowTitle(f"Detail — {fasilitas.nama}")
        self.setMinimumWidth(460)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Informasi fasilitas
        form = QFormLayout()
        form.addRow("Nama:", QLabel(self._fasilitas.nama))
        form.addRow(
            "Harga/Jam:",
            QLabel(f"Rp {int(self._fasilitas.harga_per_jam):,}"),
        )
        form.addRow(
            "Deskripsi:",
            QLabel(self._fasilitas.deskripsi or "(tidak ada deskripsi)"),
        )
        warna = "#27ae60" if self._fasilitas.status == StatusFasilitas.READY_TO_BOOK else "#e67e22"
        label_status = QLabel(self._fasilitas.status.value.replace("_", " "))
        label_status.setStyleSheet(f"color: {warna}; font-weight: bold;")
        form.addRow("Status:", label_status)
        layout.addLayout(form)

        # Tombol aksi
        baris_tombol = QHBoxLayout()

        btn_edit = QPushButton("Edit Data")
        btn_edit.clicked.connect(self._pilih_edit)

        btn_hapus = QPushButton("Hapus")
        btn_hapus.setStyleSheet("background-color: #e74c3c; color: white;")
        btn_hapus.clicked.connect(self._pilih_hapus)

        btn_tutup = QPushButton("Tutup")
        btn_tutup.clicked.connect(self.reject)

        baris_tombol.addWidget(btn_edit)
        baris_tombol.addWidget(btn_hapus)
        baris_tombol.addStretch()
        baris_tombol.addWidget(btn_tutup)
        layout.addLayout(baris_tombol)

    def _pilih_edit(self) -> None:
        self.aksi_dipilih = "edit"
        self.accept()

    def _pilih_hapus(self) -> None:
        self.aksi_dipilih = "hapus"
        self.accept()