from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPoint, QPropertyAnimation, QSequentialAnimationGroup, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_ENV_KEY = "SIRUANG_APP_PASSWORD"
_DEFAULT_PW = "admin"


def _load_env() -> None:
    """Muat variabel lingkungan dari .env di root proyek."""
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    except ImportError:
        pass


def _ambil_password() -> str:
    """Baca kata sandi aplikasi dari environment variable SIRUANG_APP_PASSWORD."""
    return os.environ.get(_ENV_KEY, _DEFAULT_PW)


class LoginDialog(QDialog):
    """Dialog autentikasi aplikasi SIRUANG. Ditampilkan sebelum MainWindow."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        _load_env()
        self._drag_pos: Optional[QPoint] = None
        self._setup_window()
        self._setup_ui()
        self._center_on_screen()

    # ------------------------------------------------------------------ #
    # Setup                                                                #
    # ------------------------------------------------------------------ #

    def _setup_window(self) -> None:
        self.setWindowTitle("SIRUANG")
        self.setFixedSize(420, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            self.move(
                rect.center().x() - self.width() // 2,
                rect.center().y() - self.height() // 2,
            )

    def paintEvent(self, event) -> None:
        """Latar belakang navy blue solid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#003773"))
        painter.end()

    def mousePressEvent(self, event) -> None:
        """Izinkan drag window untuk memindahkan dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._card = self._buat_card()
        outer.addWidget(self._card)

    def _buat_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("QFrame#loginCard { background: #ffffff; border-radius: 16px; }")

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 16)
        shadow.setColor(QColor(0, 0, 0, 55))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # Logo
        layout.addWidget(self._buat_logo(), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        # Judul
        lbl_title = QLabel("SIRUANG")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet(
            "font-size: 24px; font-weight: 800; color: #1a1a2e;"
            " letter-spacing: 3px;"
            " font-family: 'Hanken Grotesk', 'Ubuntu', 'Cantarell', sans-serif;"
        )
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Sistem Reservasi Fasilitas")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(
            "font-size: 12px; color: #94a3b8;"
            " font-family: 'Hanken Grotesk', 'Ubuntu', 'Cantarell', sans-serif;"
        )
        layout.addWidget(lbl_sub)
        layout.addSpacing(36)

        # Label kata sandi
        lbl_pw = QLabel("Kata Sandi Admin")
        lbl_pw.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #374151;"
            " font-family: 'Hanken Grotesk', 'Ubuntu', sans-serif;"
        )
        layout.addWidget(lbl_pw)
        layout.addSpacing(8)

        # Baris input: field + tombol eye
        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)

        self._pw_field = QLineEdit()
        self._pw_field.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_field.setPlaceholderText("Masukkan kata sandi...")
        self._pw_field.setFixedHeight(44)
        self._pw_field.setStyleSheet(self._gaya_field_normal())
        self._pw_field.returnPressed.connect(self._on_login)
        pw_row.addWidget(self._pw_field)

        self._btn_eye = QPushButton("◉")  # ◉
        self._btn_eye.setFixedSize(44, 44)
        self._btn_eye.setToolTip("Tampilkan/sembunyikan kata sandi")
        self._btn_eye.setStyleSheet(
            "QPushButton {"
            "  background: #f1f5f9; border: 1.5px solid #e2e8f0;"
            "  border-radius: 10px; color: #94a3b8; font-size: 16px;"
            "  padding: 0; min-height: 0;"
            "}"
            "QPushButton:hover { background: #e2e8f0; color: #475569; }"
        )
        self._btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_eye.clicked.connect(self._toggle_visibility)
        pw_row.addWidget(self._btn_eye)

        layout.addLayout(pw_row)
        layout.addSpacing(10)

        # Label error
        self._lbl_error = QLabel("")
        self._lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_error.setStyleSheet(
            "font-size: 12px; color: #ef4444; min-height: 18px;"
        )
        self._lbl_error.setVisible(False)
        layout.addWidget(self._lbl_error)
        layout.addSpacing(16)

        # Tombol masuk
        btn_masuk = QPushButton("Masuk")
        btn_masuk.setFixedHeight(46)
        btn_masuk.setStyleSheet(
            "QPushButton {"
            "  background: #003773; color: #ffffff; border: none;"
            "  border-radius: 10px; font-size: 15px; font-weight: 700;"
            "  letter-spacing: 0.5px; min-height: 0;"
            "  font-family: 'Hanken Grotesk', 'Ubuntu', sans-serif;"
            "}"
            "QPushButton:hover { background: #002555; }"
            "QPushButton:pressed { background: #001f40; }"
        )
        btn_masuk.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_masuk.clicked.connect(self._on_login)
        layout.addWidget(btn_masuk)

        return card

    def _buat_logo(self) -> QLabel:
        """Buat label berisi ikon 'S' berbentuk bulat, sesuai app icon."""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#003773"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, size, size, 16, 16)
        font = QFont("Ubuntu", 32, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
        painter.end()

        lbl = QLabel()
        lbl.setPixmap(pixmap)
        lbl.setFixedSize(size, size)
        return lbl

    # ------------------------------------------------------------------ #
    # Gaya dinamis                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _gaya_field_normal() -> str:
        return (
            "QLineEdit {"
            "  background: #f8fafc; border: 1.5px solid #e2e8f0;"
            "  border-radius: 10px; padding: 0 14px;"
            "  font-size: 14px; color: #1a1a2e;"
            "}"
            "QLineEdit:focus { border-color: #003773; background: #ffffff; }"
        )

    @staticmethod
    def _gaya_field_error() -> str:
        return (
            "QLineEdit {"
            "  background: #fff5f5; border: 1.5px solid #ef4444;"
            "  border-radius: 10px; padding: 0 14px;"
            "  font-size: 14px; color: #1a1a2e;"
            "}"
            "QLineEdit:focus { border-color: #ef4444; }"
        )

    # ------------------------------------------------------------------ #
    # Interaksi                                                            #
    # ------------------------------------------------------------------ #

    def _toggle_visibility(self) -> None:
        """Tampilkan atau sembunyikan teks kata sandi."""
        if self._pw_field.echoMode() == QLineEdit.EchoMode.Password:
            self._pw_field.setEchoMode(QLineEdit.EchoMode.Normal)
            self._btn_eye.setText("◎")  # ◎
        else:
            self._pw_field.setEchoMode(QLineEdit.EchoMode.Password)
            self._btn_eye.setText("◉")  # ◉

    def _on_login(self) -> None:
        """Validasi kata sandi dan lanjutkan atau tampilkan error."""
        if self._pw_field.text() == _ambil_password():
            self.accept()
        else:
            self._pw_field.setStyleSheet(self._gaya_field_error())
            self._pw_field.clear()
            self._lbl_error.setText("Kata sandi salah. Coba lagi.")
            self._lbl_error.setVisible(True)
            self._shake()
            QTimer.singleShot(2000, self._reset_error_state)

    def _reset_error_state(self) -> None:
        self._pw_field.setStyleSheet(self._gaya_field_normal())
        self._lbl_error.setVisible(False)

    def _shake(self) -> None:
        """Animasi goyang horizontal pada dialog saat kata sandi salah."""
        pos = self.pos()
        group = QSequentialAnimationGroup(self)
        for dx in (10, -10, 8, -8, 5, -5, 0):
            anim = QPropertyAnimation(self, b"pos")
            anim.setDuration(35)
            anim.setEndValue(QPoint(pos.x() + dx, pos.y()))
            group.addAnimation(anim)
        group.start(QSequentialAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def keyPressEvent(self, event) -> None:
        """Tutup dialog (dan keluar dari app) saat Escape ditekan."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
