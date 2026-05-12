from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
)

if TYPE_CHECKING:
    from src.controller.notifikasi_controller import NotifikasiController
    from src.entity.notifikasi import Notifikasi


class NotifikasiView(QWidget):
    """Tampilan notifikasi in-app: ikon lonceng, daftar notifikasi, dan tandai dibaca (UC14)."""

    def __init__(
        self,
        notifikasi_controller: NotifikasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._notifikasi_controller: NotifikasiController = notifikasi_controller

        self._ikon_widget: Optional[QWidget] = None
        self._badge_label: Optional[QLabel] = None
        self._bell_button: Optional[QPushButton] = None

    def tampilkan_notifikasi(self, notifikasi: Notifikasi) -> None:
        """Menampilkan pop-up atau detail pesan notifikasi in-app kepada pengelola
        mengenai reservasi yang waktu sewanya akan segera berakhir.

        Parameter:
            notifikasi: Objek Notifikasi yang akan ditampilkan.
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Notifikasi Reservasi")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(notifikasi.pesan_notifikasi)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        if not notifikasi.sudah_dibaca:
            self._notifikasi_controller.sudah_dibaca(notifikasi.id_notifikasi)
            self.update_badge()

    def tampilkan_daftar_notifikasi(self, list_notifikasi: List[Notifikasi]) -> None:
        """Menampilkan panel daftar riwayat notifikasi beserta status sudah/belum dibaca.

        Parameter:
            list_notifikasi: List objek Notifikasi yang akan ditampilkan.
        """
        dialog = _DaftarNotifikasiDialog(
            list_notifikasi=list_notifikasi,
            notifikasi_controller=self._notifikasi_controller,
            parent=self,
        )
        dialog.exec()
        self.update_badge()

    def create_navbar_icon(self, icon: Optional[QIcon] = None) -> QWidget:
        """Buat widget tombol lonceng dengan badge untuk ditempatkan di navbar.

        Returns:
            QWidget yang berisi tombol lonceng dan badge. Caller harus menambahkan widget ini ke layout navbar.
        """
        if self._ikon_widget is not None:
            return self._ikon_widget

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bell_btn = QPushButton()
        bell_btn.setFlat(True)
        bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bell_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if icon is not None:
            bell_btn.setIcon(icon)
        else:
            bell_btn.setFont(QFont("", 12))

        badge = QLabel("")
        badge.setStyleSheet(
            "QLabel { background-color: red; color: white; border-radius: 10px; padding: 1px 6px; }"
        )
        badge.setVisible(False)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("", 8, QFont.Weight.Bold))

        self._ikon_widget = container
        self._badge_label = badge
        self._bell_button = bell_btn

        bell_btn.clicked.connect(self._on_bell_clicked)

        layout.addWidget(bell_btn)
        layout.addWidget(badge)
        layout.setAlignment(bell_btn, Qt.AlignmentFlag.AlignVCenter)
        layout.setAlignment(badge, Qt.AlignmentFlag.AlignTop)

        self.update_badge()

        return container

    def update_badge(self) -> None:
        """Update angka badge berdasarkan jumlah notifikasi belum dibaca."""
        if self._badge_label is None:
            return

        try:
            daftar = self._notifikasi_controller.lihat_daftar_notifikasi()
            belum_dibaca = sum(1 for n in daftar if not n.sudah_dibaca)
        except Exception:
            belum_dibaca = 0

        if belum_dibaca > 0:
            teks = str(belum_dibaca) if belum_dibaca < 100 else "99+"
            self._badge_label.setText(teks)
            self._badge_label.setVisible(True)
        else:
            self._badge_label.setVisible(False)


    def _on_bell_clicked(self) -> None:
        """Handler saat ikon lonceng diklik: ambil daftar notifikasi dan tampilkan dialog."""
        try:
            daftar = self._notifikasi_controller.lihat_daftar_notifikasi()
        except Exception:
            daftar = []
        self.tampilkan_daftar_notifikasi(daftar)

class _DaftarNotifikasiDialog(QDialog):
    """Dialog internal untuk menampilkan daftar riwayat notifikasi."""

    def __init__(
        self,
        list_notifikasi: List[Notifikasi],
        notifikasi_controller: NotifikasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._list_notifikasi = list_notifikasi
        self._notifikasi_controller = notifikasi_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Daftar Notifikasi")
        self.setMinimumSize(550, 350)

        layout = QVBoxLayout(self)

        self._tabel = QTableWidget(0, 3)
        self._tabel.setHorizontalHeaderLabels(["Pesan", "Waktu Kirim", "Status"])
        self._tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        for notif in self._list_notifikasi:
            baris = self._tabel.rowCount()
            self._tabel.insertRow(baris)
            self._tabel.setItem(baris, 0, QTableWidgetItem(notif.pesan_notifikasi))

            waktu_text = ""
            try:
                waktu_text = notif.waktu_kirim.strftime("%d/%m/%Y %H:%M") if notif.waktu_kirim else ""
            except Exception:
                waktu_text = str(notif.waktu_kirim)

            self._tabel.setItem(baris, 1, QTableWidgetItem(waktu_text))

            status = "Dibaca" if notif.sudah_dibaca else "Belum Dibaca"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tabel.setItem(baris, 2, status_item)

        self._tabel.cellDoubleClicked.connect(self._on_cell_double_clicked)

        layout.addWidget(self._tabel)

        belum_dibaca = sum(1 for n in self._list_notifikasi if not n.sudah_dibaca)
        label = QLabel(
            f"{belum_dibaca} notifikasi belum dibaca"
            if belum_dibaca > 0 else "Semua notifikasi sudah dibaca."
        )
        layout.addWidget(label)

        tombol = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        """Tandai notifikasi yang dipilih sebagai sudah dibaca saat user double-click."""
        try:
            item = self._tabel.item(row, 0)
            if item is None:
                return
            notif_obj = None
            if row < len(self._list_notifikasi):
                notif_obj = self._list_notifikasi[row]

            if notif_obj is None:
                return

            if not notif_obj.sudah_dibaca:
                self._notifikasi_controller.sudah_dibaca(notif_obj.id_notifikasi)
                status_item = QTableWidgetItem("Dibaca")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._tabel.setItem(row, 2, status_item)
        except Exception:
            return
