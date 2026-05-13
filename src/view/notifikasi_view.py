from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
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
        """Menampilkan pop-up atau detail pesan notifikasi in-app kepada pengelola.

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
            QWidget yang berisi tombol lonceng dan badge.
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
            bell_btn.setText("Notifikasi")
            bell_btn.setProperty("nav", "true")

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

    def start_badge_pulse(self) -> None:
        """Mulai animasi denyut (pulse) tak terbatas pada badge notifikasi."""
        if self._badge_label is None:
            return
        eff = QGraphicsOpacityEffect(self._badge_label)
        self._badge_label.setGraphicsEffect(eff)
        pulse = QPropertyAnimation(eff, b"opacity", self._badge_label)
        pulse.setDuration(1000)
        pulse.setStartValue(1.0)
        pulse.setKeyValueAt(0.5, 0.5)
        pulse.setEndValue(1.0)
        pulse.setLoopCount(-1)
        pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        pulse.start()
        self._pulse_anim = pulse

    def _on_bell_clicked(self) -> None:
        """Handler saat ikon lonceng diklik: ambil daftar notifikasi dan tampilkan dialog."""
        try:
            daftar = self._notifikasi_controller.lihat_daftar_notifikasi()
        except Exception:
            daftar = []
        self.tampilkan_daftar_notifikasi(daftar)


class _NotifCard(QFrame):
    """Kartu satu notifikasi dengan klik untuk tandai dibaca."""

    def __init__(
        self,
        notif: Notifikasi,
        notifikasi_controller: NotifikasiController,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._notif = notif
        self._ctrl = notifikasi_controller
        self._is_read = notif.sudah_dibaca
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        self._dot = QLabel("●")
        self._dot.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._dot, alignment=Qt.AlignmentFlag.AlignTop)

        center = QVBoxLayout()
        center.setSpacing(4)

        self._msg_lbl = QLabel(self._notif.pesan_notifikasi)
        self._msg_lbl.setWordWrap(True)
        self._msg_lbl.setStyleSheet(
            "color: #1a1a2e; font-size: 13px; font-weight: 500;"
            " background: transparent; border: none;"
        )
        center.addWidget(self._msg_lbl)

        try:
            waktu_str = (
                self._notif.waktu_kirim.strftime("%d/%m/%Y %H:%M")
                if self._notif.waktu_kirim else ""
            )
        except Exception:
            waktu_str = str(self._notif.waktu_kirim)

        time_lbl = QLabel(waktu_str)
        time_lbl.setStyleSheet(
            "color: #94a3b8; font-size: 11px; background: transparent; border: none;"
        )
        center.addWidget(time_lbl)

        layout.addLayout(center, stretch=1)

        self._badge_lbl = QLabel()
        self._badge_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._badge_lbl, alignment=Qt.AlignmentFlag.AlignTop)

        self._update_read_state()

    def _apply_style(self) -> None:
        if self._is_read:
            self.setStyleSheet(
                "QFrame { background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }"
            )
        else:
            self.setStyleSheet(
                "QFrame { background: #eef4ff; border-radius: 10px; border: 1px solid #4182fa; }"
            )

    def _update_read_state(self) -> None:
        if self._is_read:
            self._dot.setStyleSheet("color: #cbd5e1; font-size: 10px; background: transparent;")
            self._badge_lbl.setText("Dibaca")
            self._badge_lbl.setStyleSheet(
                "color: #64748b; background: #f1f5f9; border-radius: 6px;"
                " padding: 3px 10px; font-size: 11px; font-weight: 600; border: none;"
            )
        else:
            self._dot.setStyleSheet("color: #4182fa; font-size: 10px; background: transparent;")
            self._badge_lbl.setText("Belum Dibaca")
            self._badge_lbl.setStyleSheet(
                "color: #1d4ed8; background: #dbeafe; border-radius: 6px;"
                " padding: 3px 10px; font-size: 11px; font-weight: 600; border: none;"
            )



class _DaftarNotifikasiDialog(QDialog):
    """Dialog internal untuk menampilkan daftar riwayat notifikasi sebagai kartu."""

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
        self.setMinimumSize(760, 500)

        # Tandai semua yang belum dibaca sebagai sudah dibaca saat dialog dibuka
        for n in self._list_notifikasi:
            if not n.sudah_dibaca:
                try:
                    self._notifikasi_controller.sudah_dibaca(n.id_notifikasi)
                except Exception:
                    pass
                n.sudah_dibaca = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        jumlah = len(self._list_notifikasi)
        if jumlah > 0:
            header_lbl = QLabel(f"{jumlah} notifikasi")
            header_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1a1a2e;")
        else:
            header_lbl = QLabel("Tidak ada notifikasi")
            header_lbl.setStyleSheet("font-size: 15px; font-weight: 600; color: #64748b;")
        layout.addWidget(header_lbl)

        hint_lbl = QLabel("Notifikasi otomatis ditandai dibaca saat panel ini dibuka.")
        hint_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        layout.addWidget(hint_lbl)

        # Scroll area dengan kartu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        cards_widget = QWidget()
        cards_layout = QVBoxLayout(cards_widget)
        cards_layout.setContentsMargins(0, 4, 0, 4)
        cards_layout.setSpacing(10)

        if not self._list_notifikasi:
            empty = QLabel("Tidak ada notifikasi.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            cards_layout.addWidget(empty)
        else:
            for notif in self._list_notifikasi:
                card = _NotifCard(notif, self._notifikasi_controller)
                cards_layout.addWidget(card)

        cards_layout.addStretch()
        scroll.setWidget(cards_widget)
        layout.addWidget(scroll)

        tombol = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)
