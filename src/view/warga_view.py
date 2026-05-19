from __future__ import annotations
from typing import TYPE_CHECKING, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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
        self._daftar_warga_tampil: List[Warga] = []

    def tampilkan_form_tambah_warga(self) -> None:
        """Menampilkan dialog form input data warga baru (nama, alamat, nomor HP)."""
        dialog, nama_input, alamat_input, no_hp_input, button_box = self._buat_dialog_warga(
            "Tambah Warga"
        )

        def simpan() -> None:
            nama = nama_input.text().strip()
            alamat = alamat_input.text().strip()
            no_hp = no_hp_input.text().strip()

            pesan_error = self._validasi_input_warga(nama, alamat, no_hp)
            if pesan_error:
                self.tampilkan_pesan_error("\n".join(pesan_error))
                return

            if self._warga_controller.tambah_warga(nama, alamat, no_hp):
                dialog.accept()
                self.tampilkan_pesan_berhasil("Data warga berhasil ditambahkan.")
                self.tampilkan_daftar_warga()
            else:
                self.tampilkan_pesan_error("Data warga gagal ditambahkan.")

        button_box.accepted.connect(simpan)
        button_box.rejected.connect(dialog.reject)
        dialog.exec()

    def tampilkan_daftar_warga(self) -> None:
        """Menampilkan halaman daftar warga dalam format tabel dengan fitur pencarian."""
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

        hdr = self._table_warga.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._table_warga.setColumnWidth(3, 170)
        self._table_warga.verticalHeader().setDefaultSectionSize(40)
        self._table_warga.cellDoubleClicked.connect(self._on_warga_double_click)

        root_layout.addLayout(header_layout)
        root_layout.addWidget(self._search_input)
        root_layout.addWidget(self._table_warga)

        self._isi_tabel_warga(self._warga_controller.lihat_daftar_warga())

    def _siapkan_root_layout(self) -> QVBoxLayout:
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

        self._daftar_warga_tampil = list(daftar_warga)
        self._table_warga.setRowCount(len(daftar_warga))
        for row, warga in enumerate(daftar_warga):
            self._table_warga.setItem(row, 0, QTableWidgetItem(warga.nama))
            self._table_warga.setItem(row, 1, QTableWidgetItem(warga.alamat))
            self._table_warga.setItem(row, 2, QTableWidgetItem(warga.no_hp))

            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(2, 2, 2, 2)
            aksi_layout.setSpacing(4)

            _SS_PRIMARY = (
                "QPushButton { padding: 3px 10px; min-height: 22px; border-radius: 6px;"
                " background-color: #003773; color: white; font-weight: 600;"
                " font-size: 12px; border: none; }"
                "QPushButton:hover { background-color: #002555; }"
                "QPushButton:pressed { background-color: #001f40; }"
            )
            _SS_DANGER = (
                "QPushButton { padding: 3px 10px; min-height: 22px; border-radius: 6px;"
                " background-color: #ef4444; color: white; font-weight: 600;"
                " font-size: 12px; border: none; }"
                "QPushButton:hover { background-color: #dc2626; }"
            )

            tombol_lihat = QPushButton("Lihat")
            tombol_lihat.setStyleSheet(_SS_PRIMARY)
            tombol_lihat.clicked.connect(
                lambda checked=False, id_warga=warga.id_warga: self.tampilkan_detail_warga(id_warga)
            )

            tombol_hapus = QPushButton("Hapus")
            tombol_hapus.setStyleSheet(_SS_DANGER)
            tombol_hapus.clicked.connect(
                lambda checked=False, id_warga=warga.id_warga: self._hapus_warga_dari_tabel(id_warga)
            )

            aksi_layout.addWidget(tombol_lihat)
            aksi_layout.addWidget(tombol_hapus)
            aksi_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            self._table_warga.setCellWidget(row, 3, aksi_widget)
            self._table_warga.setRowHeight(row, 40)

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

    def _on_warga_double_click(self, row: int, col: int) -> None:
        if col == 3:
            return
        if row < len(self._daftar_warga_tampil):
            self.tampilkan_detail_warga(self._daftar_warga_tampil[row].id_warga)

    def _hapus_warga_dari_tabel(self, id_warga: str) -> None:
        if not self.tampilkan_konfirmasi_hapus(id_warga):
            return

        if self._warga_controller.cek_reservasi_aktif_warga(id_warga):
            self.tampilkan_pesan_error(
                "Data warga tidak dapat dihapus karena masih memiliki reservasi aktif."
            )
            return

        if self._warga_controller.hapus_warga(id_warga):
            self.tampilkan_pesan_berhasil("Data warga berhasil dihapus.")
            self.tampilkan_daftar_warga()
        else:
            self.tampilkan_pesan_error(
                "Data warga gagal dihapus. Pastikan warga tidak memiliki reservasi aktif."
            )

    def tampilkan_detail_warga(self, id_warga: str) -> None:
        """Menampilkan halaman detail data satu warga beserta riwayat reservasinya.

        Parameter:
            id_warga: ID warga yang ingin ditampilkan detailnya.
        """
        warga = self._warga_controller.lihat_detail_warga(id_warga)
        if warga is None:
            self.tampilkan_pesan_error("Data warga tidak ditemukan.")
            return

        root_layout = self._siapkan_root_layout()

        # Header: nama warga + tombol aksi
        header_layout = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel(warga.nama)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a2e;")

        subtitle = QLabel(f"{warga.alamat} — {warga.no_hp}")
        subtitle.setStyleSheet("color: #64748b; font-size: 13px;")

        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        tombol_edit = QPushButton("Edit")
        tombol_edit.setProperty("outline", "true")
        tombol_edit.setFixedHeight(34)
        tombol_edit.clicked.connect(lambda: self.tampilkan_form_ubah_warga(id_warga))

        tombol_hapus = QPushButton("Hapus")
        tombol_hapus.setProperty("danger", "true")
        tombol_hapus.setFixedHeight(34)
        tombol_hapus.clicked.connect(lambda: self._hapus_warga_dari_tabel(id_warga))

        tombol_kembali = QPushButton("← Kembali")
        tombol_kembali.setProperty("outline", "true")
        tombol_kembali.setFixedHeight(34)
        tombol_kembali.clicked.connect(self.tampilkan_daftar_warga)

        header_layout.addWidget(tombol_edit)
        header_layout.addSpacing(4)
        header_layout.addWidget(tombol_hapus)
        header_layout.addSpacing(4)
        header_layout.addWidget(tombol_kembali)

        root_layout.addLayout(header_layout)

        # Riwayat Reservasi card
        card = QFrame()
        card.setObjectName("riwayatCard")
        card.setStyleSheet(
            "#riwayatCard { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        riwayat_title = QLabel("Riwayat Reservasi")
        riwayat_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        card_layout.addWidget(riwayat_title)

        tabel = QTableWidget()
        tabel.setColumnCount(5)
        tabel.setHorizontalHeaderLabels(["Fasilitas", "Tanggal", "Jam", "Biaya", "Status"])
        tabel.verticalHeader().setVisible(False)
        tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabel.setAlternatingRowColors(True)
        tabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        th = tabel.horizontalHeader()
        th.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        th.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        try:
            all_res = self._data_repository.get_list_reservasi()
            reservasi_warga = [r for r in all_res if r.id_warga == id_warga]
        except Exception:
            reservasi_warga = []

        if not reservasi_warga:
            tabel.setRowCount(1)
            empty_item = QTableWidgetItem("Belum ada riwayat reservasi.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabel.setItem(0, 0, empty_item)
            tabel.setSpan(0, 0, 1, 5)
        else:
            tabel.setRowCount(len(reservasi_warga))
            for row, r in enumerate(reservasi_warga):
                try:
                    fas_obj = self._data_repository.cari_fasilitas(r.id_fasilitas)
                    nama_fas = fas_obj.nama if fas_obj else r.id_fasilitas
                except Exception:
                    nama_fas = r.id_fasilitas

                tgl_str = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
                jam_str = (
                    f"{r.jam_mulai.strftime('%H:%M')}–{r.jam_selesai.strftime('%H:%M')}"
                    if r.jam_mulai and r.jam_selesai else "-"
                )
                biaya_str = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")

                tabel.setItem(row, 0, QTableWidgetItem(nama_fas))
                tabel.setItem(row, 1, QTableWidgetItem(tgl_str))
                tabel.setItem(row, 2, QTableWidgetItem(jam_str))
                tabel.setItem(row, 3, QTableWidgetItem(biaya_str))

                if r.status.value == "LUNAS":
                    st_item = QTableWidgetItem("LUNAS")
                    st_item.setForeground(QColor("#166534"))
                    st_item.setBackground(QColor("#dcfce7"))
                else:
                    st_item = QTableWidgetItem("BELUM DIBAYAR")
                    st_item.setForeground(QColor("#92400e"))
                    st_item.setBackground(QColor("#fef3c7"))
                st_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, 4, st_item)

        def _buka_detail_reservasi(row: int, col: int, res_list=reservasi_warga) -> None:
            if row >= len(res_list):
                return
            r = res_list[row]
            try:
                fas_obj = self._data_repository.cari_fasilitas(r.id_fasilitas)
                nama_fas = fas_obj.nama if fas_obj else r.id_fasilitas
            except Exception:
                nama_fas = r.id_fasilitas
            tgl = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
            jam = (
                f"{r.jam_mulai.strftime('%H:%M')} – {r.jam_selesai.strftime('%H:%M')}"
                if r.jam_mulai and r.jam_selesai else "-"
            )
            biaya = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")
            status = r.status.value
            d = QDialog(self)
            d.setWindowTitle("Detail Reservasi")
            d.setMinimumWidth(380)
            fl = QFormLayout(d)
            fl.setSpacing(10)
            fl.addRow("Fasilitas:", QLabel(nama_fas))
            fl.addRow("Tanggal:", QLabel(tgl))
            fl.addRow("Jam:", QLabel(jam))
            fl.addRow("Total Biaya:", QLabel(biaya))
            fl.addRow("Status:", QLabel(status))
            btn_tutup = QPushButton("Tutup")
            btn_tutup.setProperty("outline", "true")
            btn_tutup.clicked.connect(d.accept)
            fl.addRow(btn_tutup)
            d.exec()

        tabel.cellDoubleClicked.connect(_buka_detail_reservasi)
        card_layout.addWidget(tabel)
        root_layout.addWidget(card)

    def tampilkan_form_ubah_warga(self, id_warga: str) -> None:
        """Menampilkan form edit dengan data warga yang sudah ada sebagai nilai awal.

        Parameter:
            id_warga: ID warga yang datanya akan diubah.
        """
        warga = self._warga_controller.lihat_detail_warga(id_warga)
        if warga is None:
            self.tampilkan_pesan_error("Data warga tidak ditemukan.")
            return

        dialog, nama_input, alamat_input, no_hp_input, button_box = self._buat_dialog_warga(
            "Edit Warga", warga.nama, warga.alamat, warga.no_hp
        )

        def simpan() -> None:
            nama = nama_input.text().strip()
            alamat = alamat_input.text().strip()
            no_hp = no_hp_input.text().strip()

            pesan_error = self._validasi_input_warga(nama, alamat, no_hp)
            if pesan_error:
                self.tampilkan_pesan_error("\n".join(pesan_error))
                return

            if self._warga_controller.ubah_warga(id_warga, nama, alamat, no_hp):
                dialog.accept()
                self.tampilkan_pesan_berhasil("Data warga berhasil diperbarui.")
                self.tampilkan_daftar_warga()
            else:
                self.tampilkan_pesan_error("Data warga gagal diperbarui.")

        button_box.accepted.connect(simpan)
        button_box.rejected.connect(dialog.reject)
        dialog.exec()

    def _buat_dialog_warga(
        self,
        judul: str,
        nama: str = "",
        alamat: str = "",
        no_hp: str = "",
    ) -> tuple[QDialog, QLineEdit, QLineEdit, QLineEdit, QDialogButtonBox]:
        dialog = QDialog(self)
        dialog.setWindowTitle(judul)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        nama_input = QLineEdit(nama)
        alamat_input = QLineEdit(alamat)
        no_hp_input = QLineEdit(no_hp)
        no_hp_input.setPlaceholderText("10-13 digit angka")

        form_layout.addRow("Nama", nama_input)
        form_layout.addRow("Alamat", alamat_input)
        form_layout.addRow("No. HP", no_hp_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("Simpan")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Batal")

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        return dialog, nama_input, alamat_input, no_hp_input, button_box

    def _validasi_input_warga(self, nama: str, alamat: str, no_hp: str) -> List[str]:
        pesan_error: List[str] = []
        if not nama:
            pesan_error.append("Nama tidak boleh kosong.")
        if not alamat:
            pesan_error.append("Alamat tidak boleh kosong.")
        if not no_hp:
            pesan_error.append("No. HP tidak boleh kosong.")
        elif not no_hp.isdigit():
            pesan_error.append("No. HP hanya boleh berisi angka.")
        elif not 10 <= len(no_hp) <= 13:
            pesan_error.append("No. HP harus terdiri dari 10 sampai 13 digit.")
        elif not self._warga_controller.validasi_data_warga(nama, alamat, no_hp):
            pesan_error.append("Data warga tidak valid.")
        return pesan_error

    def tampilkan_konfirmasi_hapus(self, id_warga: str) -> bool:
        """Menampilkan dialog konfirmasi sebelum proses penghapusan warga dijalankan.

        Parameter:
            id_warga: ID warga yang akan dihapus.

        Returns:
            True jika pengelola mengkonfirmasi penghapusan, False jika batal.
        """
        warga = self._warga_controller.lihat_detail_warga(id_warga)
        nama_warga = warga.nama if warga is not None else id_warga

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Konfirmasi Hapus")
        dialog.setText(f"Apakah Anda yakin ingin menghapus data warga {nama_warga}?")
        tombol_ya = dialog.addButton("Ya", QMessageBox.ButtonRole.YesRole)
        dialog.addButton("Batal", QMessageBox.ButtonRole.RejectRole)
        dialog.setDefaultButton(tombol_ya)
        dialog.exec()

        return dialog.clickedButton() == tombol_ya

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
