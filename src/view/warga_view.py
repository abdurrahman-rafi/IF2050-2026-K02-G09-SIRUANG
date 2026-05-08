from __future__ import annotations
from typing import TYPE_CHECKING, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.controller.warga_controller import WargaController
    from src.data.data_repository import DataRepository
    from src.entity.warga import Warga


class WargaView(QWidget):
    """Tampilan pengelolaan data warga: daftar, tambah, detail, edit, dan hapus (UC01-UC04)."""

    def __init__(
        self,
        warga_controller: WargaController,
        data_repository: DataRepository,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._warga_controller: WargaController = warga_controller
        self._data_repository: DataRepository = data_repository
        self._search_input: QLineEdit | None = None
        self._table_warga: QTableWidget | None = None

    # TODO
    def tampilkan_form_tambah_warga(self) -> None:
        """Menampilkan dialog form input data warga baru (nama, alamat, nomor HP)."""
        pass

    def tampilkan_daftar_warga(self) -> None:
        """Menampilkan halaman daftar warga dalam format tabel dengan fitur pencarian
        berdasarkan nama, alamat, atau nomor HP."""
        root_layout = self._siapkan_root_layout()

        header_layout = QHBoxLayout()
        title = QLabel("Daftar Warga")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")

        tombol_tambah = QPushButton("+ Tambah Warga")
        tombol_tambah.clicked.connect(self.tampilkan_form_tambah_warga)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(tombol_tambah)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Cari berdasarkan nama, alamat, atau no. HP")
        self._search_input.textChanged.connect(self._filter_tabel_warga)

        self._table_warga = QTableWidget()
        self._table_warga.setColumnCount(4)
        self._table_warga.setHorizontalHeaderLabels(["Nama", "Alamat", "No. HP", "Aksi"])
        self._table_warga.verticalHeader().setVisible(False)
        self._table_warga.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table_warga.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table_warga.setAlternatingRowColors(True)
        self._table_warga.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table_warga.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table_warga.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table_warga.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )

        root_layout.addLayout(header_layout)
        root_layout.addWidget(self._search_input)
        root_layout.addWidget(self._table_warga)

        self._isi_tabel_warga(self._warga_controller.lihat_daftar_warga())

    def _siapkan_root_layout(self) -> QVBoxLayout:
        """Menyiapkan layout utama dan membersihkan konten lama."""
        layout = self.layout()
        if layout is None:
            root_layout = QVBoxLayout(self)
        else:
            root_layout = layout

        while root_layout.count():
            self._hapus_item_layout(root_layout.takeAt(0))

        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)
        return root_layout

    def _hapus_item_layout(self, item) -> None:
        child_layout = item.layout()
        if child_layout is not None:
            while child_layout.count():
                self._hapus_item_layout(child_layout.takeAt(0))

        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    def _isi_tabel_warga(self, daftar_warga: List[Warga]) -> None:
        if self._table_warga is None:
            return

        self._table_warga.setRowCount(len(daftar_warga))
        for row, warga in enumerate(daftar_warga):
            self._table_warga.setItem(row, 0, QTableWidgetItem(warga.nama))
            self._table_warga.setItem(row, 1, QTableWidgetItem(warga.alamat))
            self._table_warga.setItem(row, 2, QTableWidgetItem(warga.no_hp))

            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(0, 0, 0, 0)
            aksi_layout.setSpacing(8)

            tombol_lihat = QPushButton("Lihat")
            tombol_lihat.clicked.connect(
                lambda checked=False, id_warga=warga.id_warga: self.tampilkan_detail_warga(
                    id_warga
                )
            )

            tombol_hapus = QPushButton("Hapus")
            tombol_hapus.clicked.connect(
                lambda checked=False, id_warga=warga.id_warga: self._hapus_warga_dari_tabel(
                    id_warga
                )
            )

            aksi_layout.addWidget(tombol_lihat)
            aksi_layout.addWidget(tombol_hapus)
            aksi_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table_warga.setCellWidget(row, 3, aksi_widget)

    def _filter_tabel_warga(self, keyword: str) -> None:
        keyword = keyword.strip().lower()
        daftar_warga = self._warga_controller.lihat_daftar_warga()
        if keyword:
            daftar_warga = [
                warga
                for warga in daftar_warga
                if keyword in warga.nama.lower()
                or keyword in warga.alamat.lower()
                or keyword in warga.no_hp.lower()
            ]

        self._isi_tabel_warga(daftar_warga)

    def _hapus_warga_dari_tabel(self, id_warga: str) -> None:
        if not self.tampilkan_konfirmasi_hapus(id_warga):
            return

        if self._warga_controller.hapus_warga(id_warga):
            self.tampilkan_pesan_berhasil("Data warga berhasil dihapus.")
            self._filter_tabel_warga(self._search_input.text() if self._search_input else "")
        else:
            self.tampilkan_pesan_error(
                "Data warga gagal dihapus. Pastikan warga tidak memiliki reservasi aktif."
            )

    def tampilkan_detail_warga(self, id_warga: str) -> None:
        """Menampilkan halaman detail data satu warga berdasarkan ID.

        Parameter:
            id_warga: ID warga yang ingin ditampilkan detailnya.
        """
        warga = self._warga_controller.lihat_detail_warga(id_warga)
        if warga is None:
            self.tampilkan_pesan_error("Data warga tidak ditemukan.")
            return

        root_layout = self._siapkan_root_layout()

        header_layout = QHBoxLayout()
        title = QLabel("Detail Warga")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")

        tombol_kembali = QPushButton("Kembali")
        tombol_kembali.clicked.connect(self.tampilkan_daftar_warga)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(tombol_kembali)

        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(8)
        detail_layout.addWidget(QLabel(f"Nama: {warga.nama}"))
        detail_layout.addWidget(QLabel(f"Alamat: {warga.alamat}"))
        detail_layout.addWidget(QLabel(f"No. HP: {warga.no_hp}"))

        root_layout.addLayout(header_layout)
        root_layout.addLayout(detail_layout)
        root_layout.addStretch()

    # TODO
    def tampilkan_form_ubah_warga(self, id_warga: str) -> None:
        """Menampilkan form edit dengan data warga yang sudah ada sebagai nilai awal.

        Parameter:
            id_warga: ID warga yang datanya akan diubah.
        """
        pass

    def tampilkan_konfirmasi_hapus(self, id_warga: str) -> bool:
        """Menampilkan dialog konfirmasi sebelum proses penghapusan warga dijalankan.

        Parameter:
            id_warga: ID warga yang akan dihapus.

        Returns:
            True jika pengelola mengkonfirmasi penghapusan, False jika batal.
        """
        warga = self._warga_controller.lihat_detail_warga(id_warga)
        nama_warga = warga.nama if warga is not None else id_warga

        jawaban = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus data warga {nama_warga}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return jawaban == QMessageBox.StandardButton.Yes

    def tampilkan_pesan_berhasil(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan sukses setelah operasi berhasil diproses.

        Parameter:
            pesan: Teks pesan sukses yang akan ditampilkan.
        """
        QMessageBox.information(self, "Berhasil", pesan)

    def tampilkan_pesan_error(self, pesan: str) -> None:
        """Menampilkan dialog notifikasi pesan error jika validasi atau operasi gagal.

        Parameter:
            pesan: Teks pesan error yang akan ditampilkan.
        """
        QMessageBox.warning(self, "Gagal", pesan)
