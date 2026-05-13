from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import (
    QAbstractAnimation, QDate, QEasingCurve, QPropertyAnimation, Qt, QTime, QTimer,
)
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from src.controller.fasilitas_controller import FasilitasController
from src.entity.enums import StatusFasilitas, StatusReservasi

if TYPE_CHECKING:
    from src.controller.reservasi_controller import ReservasiController
    from src.data.data_repository import DataRepository
    from src.entity.fasilitas import Fasilitas

_IMG_DIR = Path(__file__).parent.parent.parent / "img"

_IMG_H = 160   # tinggi area gambar / gradien
_CARD_MIN_W = 240


class _CardImage(QWidget):
    """Header kartu: gambar (jika ada) atau gradien dengan inisial nama fasilitas."""

    def __init__(self, fasilitas: "Fasilitas", parent: QWidget = None) -> None:
        super().__init__(parent)
        self._fasilitas = fasilitas
        self.setFixedHeight(_IMG_H)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clip hanya sudut atas (radius 12px)
        path = QPainterPath()
        r = self.rect()
        radius = 12.0
        path.moveTo(r.left() + radius, r.top())
        path.lineTo(r.right() - radius, r.top())
        path.quadTo(r.right(), r.top(), r.right(), r.top() + radius)
        path.lineTo(r.right(), r.bottom())
        path.lineTo(r.left(), r.bottom())
        path.lineTo(r.left(), r.top() + radius)
        path.quadTo(r.left(), r.top(), r.left() + radius, r.top())
        path.closeSubpath()
        p.setClipPath(path)

        gambar_path = _IMG_DIR / self._fasilitas.gambar if self._fasilitas.gambar else None
        if gambar_path and gambar_path.exists():
            pm = QPixmap(str(gambar_path)).scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            p.drawPixmap(0, 0, pm)
        else:
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor("#003773"))
            grad.setColorAt(1.0, QColor("#4182fa"))
            p.fillRect(r, grad)

            # Inisial nama fasilitas sebagai ikon
            font = QFont()
            font.setPointSize(36)
            font.setBold(True)
            p.setFont(font)
            p.setPen(QColor(255, 255, 255, 170))
            initial = self._fasilitas.nama[0].upper() if self._fasilitas.nama else "F"
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, initial)

        p.end()


class _FasilitasCard(QFrame):
    """Kartu fasilitas dengan shadow hover dan mousePressEvent."""

    def __init__(self, on_click, shadow: QGraphicsDropShadowEffect, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._on_click = on_click
        self._shadow = shadow

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self._on_click()

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        if self.graphicsEffect() is self._shadow:
            self._shadow.setBlurRadius(26)
            self._shadow.setOffset(0, 7)
            self._shadow.setColor(QColor(0, 0, 0, 28))

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        if self.graphicsEffect() is self._shadow:
            self._shadow.setBlurRadius(16)
            self._shadow.setOffset(0, 2)
            self._shadow.setColor(QColor(0, 0, 0, 20))


class FasilitasView(QWidget):
    """Tampilan pengelolaan data fasilitas: landing page, tambah, detail, edit, hapus (UC05-UC08)."""

    def __init__(
        self,
        data_repository: DataRepository,
        reservasi_controller: Optional[ReservasiController] = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._data_repository = data_repository
        self._controller = FasilitasController(data_repository)
        self._reservasi_ctrl: Optional[ReservasiController] = reservasi_controller
        self._semua_fasilitas: List[Fasilitas] = []
        self._inner_stack: Optional[QStackedWidget] = None
        self._setup_ui()
        self._muat_fasilitas()

    # ------------------------------------------------------------------ #
    # Setup awal UI                                                        #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._inner_stack = QStackedWidget()
        outer.addWidget(self._inner_stack)

        self._inner_stack.addWidget(self._buat_list_page())

    def _buat_list_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        judul = QLabel("Manajemen Fasilitas")
        judul.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a2e;")
        header.addWidget(judul)
        header.addStretch()
        btn_tambah = QPushButton("+ Tambah Fasilitas")
        btn_tambah.setFixedHeight(36)
        btn_tambah.clicked.connect(self.tampilkan_form_tambah_fasilitas)
        header.addWidget(btn_tambah)
        layout.addLayout(header)

        # Filter
        baris_filter = QHBoxLayout()
        self._input_cari = QLineEdit()
        self._input_cari.setPlaceholderText("Cari nama fasilitas...")
        self._input_cari.setFixedHeight(34)
        self._input_cari.textChanged.connect(self._terapkan_filter)
        baris_filter.addWidget(self._input_cari)

        self._combo_status = QComboBox()
        self._combo_status.setFixedHeight(34)
        self._combo_status.setMinimumWidth(160)
        self._combo_status.addItem("Semua Status", None)
        for s in StatusFasilitas:
            self._combo_status.addItem(s.value.replace("_", " "), s)
        self._combo_status.currentIndexChanged.connect(self._terapkan_filter)
        baris_filter.addWidget(self._combo_status)
        layout.addLayout(baris_filter)

        # Grid kartu
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(20)
        self._grid.setContentsMargins(0, 8, 0, 8)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        return page

    # ------------------------------------------------------------------ #
    # Halaman detail (full page)                                           #
    # ------------------------------------------------------------------ #

    def _ke_daftar(self) -> None:
        if self._inner_stack is not None:
            self._inner_stack.setCurrentIndex(0)
            self._muat_fasilitas()

    def _tampilkan_halaman_detail(self, fasilitas: Fasilitas) -> None:
        if self._inner_stack is None:
            return
        if self._inner_stack.count() > 1:
            old = self._inner_stack.widget(1)
            self._inner_stack.removeWidget(old)
            old.deleteLater()
        detail_page = self._buat_halaman_detail(fasilitas)
        self._inner_stack.addWidget(detail_page)
        self._inner_stack.setCurrentIndex(1)

    def _buat_halaman_detail(self, fasilitas: Fasilitas) -> QWidget:
        """Membangun halaman detail fasilitas dengan form reservasi dan riwayat."""
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        if fasilitas.status == StatusFasilitas.READY_TO_BOOK:
            status_txt = "TERSEDIA"
            badge_css = (
                "color: #166534; background: #dcfce7; border-radius: 10px;"
                " padding: 2px 10px; font-size: 11px; font-weight: 700; border: none;"
            )
        else:
            status_txt = "MAINTENANCE"
            badge_css = (
                "color: #92400e; background: #fef3c7; border-radius: 10px;"
                " padding: 2px 10px; font-size: 11px; font-weight: 700; border: none;"
            )

        harga_str = "Rp " + f"{int(fasilitas.harga_per_jam):,}".replace(",", ".")

        hdr = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(6)

        title_lbl = QLabel(fasilitas.nama)
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a2e;")

        subtitle_row = QHBoxLayout()
        subtitle_row.setSpacing(8)
        badge_status = QLabel(status_txt)
        badge_status.setStyleSheet(badge_css)
        badge_status.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sep_lbl = QLabel(f"— {harga_str}/jam")
        sep_lbl.setStyleSheet("color: #64748b; font-size: 13px;")
        subtitle_row.addWidget(badge_status)
        subtitle_row.addWidget(sep_lbl)
        subtitle_row.addStretch()

        title_col.addWidget(title_lbl)
        title_col.addLayout(subtitle_row)
        hdr.addLayout(title_col)
        hdr.addStretch()

        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("outline", "true")
        btn_edit.setFixedHeight(34)
        btn_edit.clicked.connect(lambda: self.tampilkan_form_ubah_fasilitas(fasilitas))

        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("danger", "true")
        btn_hapus.setFixedHeight(34)
        btn_hapus.clicked.connect(lambda: self.tampilkan_konfirmasi_hapus(fasilitas))

        btn_kembali = QPushButton("← Kembali")
        btn_kembali.setProperty("outline", "true")
        btn_kembali.setFixedHeight(34)
        btn_kembali.clicked.connect(self._ke_daftar)

        hdr.addWidget(btn_edit)
        hdr.addSpacing(6)
        hdr.addWidget(btn_hapus)
        hdr.addSpacing(6)
        hdr.addWidget(btn_kembali)
        layout.addLayout(hdr)

        # Detail card (full width)
        detail_card = self._buat_card()
        dc_layout = QGridLayout()
        dc_layout.setHorizontalSpacing(40)
        dc_layout.setVerticalSpacing(16)

        fields = [
            ("NAMA FASILITAS", fasilitas.nama),
            ("STATUS", status_txt),
            ("HARGA PER JAM", harga_str),
            ("DESKRIPSI", fasilitas.deskripsi or "(tidak ada deskripsi)"),
        ]
        for idx, (lbl_txt, val_txt) in enumerate(fields):
            grp = QVBoxLayout()
            grp.setSpacing(3)
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;"
                " background: transparent; border: none;"
            )
            val = QLabel(val_txt)
            val.setStyleSheet(
                "font-size: 14px; font-weight: 500; color: #1a1a2e;"
                " background: transparent; border: none;"
            )
            val.setWordWrap(True)
            grp.addWidget(lbl)
            grp.addWidget(val)
            dc_layout.addLayout(grp, idx // 2, idx % 2)

        dc_inner = QWidget()
        dc_inner.setLayout(dc_layout)
        dc_inner.setStyleSheet("background: transparent;")
        detail_card_outer = QVBoxLayout(detail_card)
        detail_card_outer.setContentsMargins(24, 20, 24, 20)
        detail_card_outer.addWidget(dc_inner)
        layout.addWidget(detail_card)

        # Two-column row
        two_col = QHBoxLayout()
        two_col.setSpacing(20)

        # Left: Buat Reservasi
        left_card = self._buat_card()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 20, 24, 20)
        left_layout.setSpacing(14)

        form_title = QLabel("Buat Reservasi")
        form_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        left_layout.addWidget(form_title)

        combo_warga = QComboBox()
        try:
            daftar_warga = self._data_repository.get_warga_list()
            combo_warga.addItem("-- Pilih Warga --", None)
            for w in daftar_warga:
                combo_warga.addItem(w.nama, w.id_warga)
        except Exception:
            combo_warga.addItem("-- Pilih Warga --", None)

        input_tanggal = QDateEdit(QDate.currentDate())
        input_tanggal.setCalendarPopup(True)

        input_jam_mulai = QTimeEdit(QTime(9, 0))
        input_jam_selesai = QTimeEdit(QTime(11, 0))

        lbl_estimasi = QLabel("Estimasi Total: " + harga_str)
        lbl_estimasi.setStyleSheet(
            "background: #eef4ff; border: 1.5px solid #4182fa; border-radius: 8px;"
            " padding: 10px 16px; font-size: 15px; font-weight: 700; color: #003773;"
        )
        lbl_estimasi.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def hitung_estimasi() -> None:
            t_mulai = input_jam_mulai.time().toPyTime()
            t_selesai = input_jam_selesai.time().toPyTime()
            menit = (t_selesai.hour * 60 + t_selesai.minute) - (t_mulai.hour * 60 + t_mulai.minute)
            if menit <= 0:
                lbl_estimasi.setText("Jam selesai harus lebih dari jam mulai")
                return
            total = (Decimal(str(menit)) / Decimal("60")) * fasilitas.harga_per_jam
            total_str = "Rp " + f"{int(total):,}".replace(",", ".")
            lbl_estimasi.setText(f"Estimasi Total: {total_str}")

        input_jam_mulai.timeChanged.connect(lambda _: hitung_estimasi())
        input_jam_selesai.timeChanged.connect(lambda _: hitung_estimasi())
        hitung_estimasi()

        spin_jam_notif = QSpinBox()
        spin_jam_notif.setRange(1, 24)
        spin_jam_notif.setValue(
            self._reservasi_ctrl.get_jam_notifikasi() if self._reservasi_ctrl else 2
        )
        spin_jam_notif.setSuffix(" jam sebelum berakhir")

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.addRow("Pilih Warga", combo_warga)
        form.addRow("Tanggal", input_tanggal)
        form.addRow("Jam Mulai", input_jam_mulai)
        form.addRow("Jam Selesai", input_jam_selesai)
        form.addRow("Notifikasi", spin_jam_notif)
        left_layout.addLayout(form)
        left_layout.addWidget(lbl_estimasi)
        left_layout.addStretch()

        btn_simpan_res = QPushButton("Simpan Reservasi")
        btn_simpan_res.setFixedHeight(38)

        def proses_simpan() -> None:
            if self._reservasi_ctrl is None:
                self.tampilkan_pesan_error("Fitur reservasi tidak tersedia.")
                return
            id_warga_val = combo_warga.currentData()
            if id_warga_val is None:
                self.tampilkan_pesan_error("Pilih warga terlebih dahulu.")
                return
            berhasil = self._reservasi_ctrl.tambah_reservasi(
                id_warga_val,
                fasilitas.id_fasilitas,
                input_tanggal.date().toPyDate(),
                input_jam_mulai.time().toPyTime(),
                input_jam_selesai.time().toPyTime(),
                spin_jam_notif.value(),
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Reservasi berhasil ditambahkan!")
                self._tampilkan_halaman_detail(fasilitas)
            else:
                self.tampilkan_pesan_error(
                    "Gagal menambahkan reservasi.\n"
                    "Pastikan jadwal tidak bentrok dan jam selesai > jam mulai."
                )

        btn_simpan_res.clicked.connect(proses_simpan)
        left_layout.addWidget(btn_simpan_res)

        # Right: Riwayat Reservasi
        right_card = self._buat_card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(14)

        riwayat_title = QLabel("Riwayat Reservasi")
        riwayat_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        right_layout.addWidget(riwayat_title)

        riwayat_tabel = QTableWidget()
        riwayat_tabel.setColumnCount(5)
        riwayat_tabel.setHorizontalHeaderLabels(["Warga", "Tanggal", "Jam", "Biaya", "Status"])
        riwayat_tabel.verticalHeader().setVisible(False)
        riwayat_tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        riwayat_tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        riwayat_tabel.setAlternatingRowColors(True)
        riwayat_tabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        rh = riwayat_tabel.horizontalHeader()
        rh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        rh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        rh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        rh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        rh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        riwayat_tabel.verticalHeader().setDefaultSectionSize(44)

        try:
            riwayat = self._data_repository.cari_reservasi_by_fasilitas(fasilitas.id_fasilitas)
        except Exception:
            riwayat = []

        if not riwayat:
            riwayat_tabel.setRowCount(1)
            empty_item = QTableWidgetItem("Belum ada riwayat reservasi.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            riwayat_tabel.setItem(0, 0, empty_item)
            riwayat_tabel.setSpan(0, 0, 1, 5)
        else:
            riwayat_tabel.setRowCount(len(riwayat))
            for row, r in enumerate(riwayat):
                try:
                    warga_obj = self._data_repository.cari_warga(r.id_warga)
                    nama_warga = warga_obj.nama if warga_obj else r.id_warga
                except Exception:
                    nama_warga = r.id_warga

                tgl_str = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
                jam_str = (
                    f"{r.jam_mulai.strftime('%H:%M')}–{r.jam_selesai.strftime('%H:%M')}"
                    if r.jam_mulai and r.jam_selesai else "-"
                )
                biaya_str = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")

                riwayat_tabel.setItem(row, 0, QTableWidgetItem(nama_warga))
                riwayat_tabel.setItem(row, 1, QTableWidgetItem(tgl_str))
                riwayat_tabel.setItem(row, 2, QTableWidgetItem(jam_str))
                riwayat_tabel.setItem(row, 3, QTableWidgetItem(biaya_str))

                if r.status == StatusReservasi.LUNAS:
                    st_item = QTableWidgetItem("LUNAS")
                    st_item.setForeground(QColor("#166534"))
                    st_item.setBackground(QColor("#dcfce7"))
                else:
                    st_item = QTableWidgetItem("BELUM DIBAYAR")
                    st_item.setForeground(QColor("#92400e"))
                    st_item.setBackground(QColor("#fef3c7"))
                st_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                riwayat_tabel.setItem(row, 4, st_item)

        def _buka_detail_reservasi_fasilitas(row: int, col: int, res_list=riwayat) -> None:
            if row >= len(res_list):
                return
            r = res_list[row]
            try:
                warga_obj = self._data_repository.cari_warga(r.id_warga)
                nama_w = warga_obj.nama if warga_obj else r.id_warga
            except Exception:
                nama_w = r.id_warga
            tgl = r.tanggal_dibuat.strftime("%d/%m/%Y") if r.tanggal_dibuat else "-"
            jam = (
                f"{r.jam_mulai.strftime('%H:%M')} – {r.jam_selesai.strftime('%H:%M')}"
                if r.jam_mulai and r.jam_selesai else "-"
            )
            biaya = "Rp " + f"{int(r.total_biaya):,}".replace(",", ".")
            d = QDialog(self)
            d.setWindowTitle("Detail Reservasi")
            d.setMinimumWidth(380)
            fl = QFormLayout(d)
            fl.setSpacing(10)
            fl.addRow("Warga:", QLabel(nama_w))
            fl.addRow("Tanggal:", QLabel(tgl))
            fl.addRow("Jam:", QLabel(jam))
            fl.addRow("Total Biaya:", QLabel(biaya))
            fl.addRow("Status:", QLabel(r.status.value))
            btn_tutup = QPushButton("Tutup")
            btn_tutup.setProperty("outline", "true")
            btn_tutup.clicked.connect(d.accept)
            fl.addRow(btn_tutup)
            d.exec()

        riwayat_tabel.cellDoubleClicked.connect(_buka_detail_reservasi_fasilitas)
        right_layout.addWidget(riwayat_tabel)

        two_col.addWidget(left_card, 1)
        two_col.addWidget(right_card, 1)
        layout.addLayout(two_col)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)
        return page

    def _buat_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        return card

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

    def _buat_kartu(self, fasilitas: Fasilitas) -> _FasilitasCard:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))

        card = _FasilitasCard(
            on_click=lambda f=fasilitas: self.tampilkan_detail_fasilitas(f),
            shadow=shadow,
        )
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setMinimumWidth(_CARD_MIN_W)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setToolTip("Klik untuk melihat detail")
        card.setStyleSheet(
            "QFrame { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }"
        )
        card.setGraphicsEffect(shadow)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        card_image = _CardImage(fasilitas, card)
        card_image.setFixedHeight(_IMG_H)
        outer.addWidget(card_image)

        body = QWidget()
        body.setStyleSheet("background: #ffffff; border: none;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 14, 16, 16)
        body_layout.setSpacing(4)

        label_nama = QLabel(fasilitas.nama)
        label_nama.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #1a1a2e; background: transparent;"
        )
        label_nama.setWordWrap(True)

        harga_str = "Rp " + f"{int(fasilitas.harga_per_jam):,}".replace(",", ".") + "/jam"
        label_harga = QLabel(harga_str)
        label_harga.setStyleSheet(
            "color: #4182fa; font-size: 13px; font-weight: 600; background: transparent;"
        )

        body_layout.addWidget(label_nama)
        body_layout.addWidget(label_harga)

        if fasilitas.deskripsi:
            body_layout.addSpacing(4)
            label_desc = QLabel(fasilitas.deskripsi)
            label_desc.setStyleSheet(
                "color: #64748b; font-size: 12px; background: transparent;"
            )
            label_desc.setWordWrap(True)
            body_layout.addWidget(label_desc)

        body_layout.addSpacing(10)

        if fasilitas.status == StatusFasilitas.READY_TO_BOOK:
            teks_status, warna_fg, warna_bg = "TERSEDIA", "#166534", "#dcfce7"
        else:
            teks_status, warna_fg, warna_bg = "MAINTENANCE", "#92400e", "#fef3c7"

        label_status = QLabel(teks_status)
        label_status.setStyleSheet(
            f"color: {warna_fg}; background: {warna_bg}; border-radius: 10px;"
            " padding: 3px 10px; font-size: 11px; font-weight: 700; border: none;"
        )
        label_status.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        label_status.adjustSize()

        body_layout.addWidget(label_status)
        outer.addWidget(body)

        return card

    def _fade_in_card(self, card: _FasilitasCard) -> None:
        shadow = card._shadow
        eff = QGraphicsOpacityEffect(card)
        card.setGraphicsEffect(eff)
        eff.setOpacity(0.0)

        anim = QPropertyAnimation(eff, b"opacity", card)
        anim.setDuration(200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: card.setGraphicsEffect(shadow))
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    # ------------------------------------------------------------------ #
    # Metode publik                                                        #
    # ------------------------------------------------------------------ #

    def tampilkan_daftar_fasilitas(self, daftar_fasilitas: List[Fasilitas]) -> None:
        """Menampilkan landing page daftar fasilitas dalam format card grid."""
        self._bersihkan_grid()

        if not daftar_fasilitas:
            frame_kosong = QFrame()
            frame_kosong.setStyleSheet("background: transparent; border: none;")
            kosong_layout = QVBoxLayout(frame_kosong)
            kosong_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            kosong_layout.setSpacing(8)

            judul_kosong = QLabel("Belum ada fasilitas")
            judul_kosong.setStyleSheet(
                "font-size: 16px; font-weight: 700; color: #1a1a2e;"
                " background: transparent; border: none;"
            )
            judul_kosong.setAlignment(Qt.AlignmentFlag.AlignCenter)

            sub_kosong = QLabel("Klik '+ Tambah Fasilitas' untuk menambahkan.")
            sub_kosong.setStyleSheet(
                "font-size: 13px; color: #64748b; background: transparent; border: none;"
            )
            sub_kosong.setAlignment(Qt.AlignmentFlag.AlignCenter)

            kosong_layout.addWidget(judul_kosong)
            kosong_layout.addWidget(sub_kosong)
            self._grid.addWidget(frame_kosong, 0, 0)
            return

        jumlah_kolom = 3
        for i, fasilitas in enumerate(daftar_fasilitas):
            kartu = self._buat_kartu(fasilitas)
            self._grid.addWidget(kartu, i // jumlah_kolom, i % jumlah_kolom)

        # Isi kolom kosong agar distribusi rata
        remainder = len(daftar_fasilitas) % jumlah_kolom
        if remainder:
            last_row = len(daftar_fasilitas) // jumlah_kolom
            for c in range(remainder, jumlah_kolom):
                spacer_w = QWidget()
                spacer_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                spacer_w.setStyleSheet("background: transparent;")
                self._grid.addWidget(spacer_w, last_row, c)

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
                data.get("gambar", ""),
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
        self._tampilkan_halaman_detail(fasilitas)

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
                data.get("gambar", ""),
            )
            if berhasil:
                self.tampilkan_pesan_berhasil("Fasilitas berhasil diperbarui.")
                self._ke_daftar()
            else:
                self.tampilkan_pesan_error(
                    "Gagal memperbarui fasilitas. Periksa kembali data yang dimasukkan."
                )

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
                self._ke_daftar()
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
# Dialog pembantu                                                       #
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

        self._input_gambar = QLineEdit()
        self._input_gambar.setPlaceholderText("Contoh: aula.jpg")

        self._input_status = QComboBox()
        for s in StatusFasilitas:
            self._input_status.addItem(s.value.replace("_", " "), s)

        if fasilitas is not None:
            self._input_nama.setText(fasilitas.nama)
            self._input_harga.setValue(float(fasilitas.harga_per_jam))
            self._input_deskripsi.setPlainText(fasilitas.deskripsi or "")
            self._input_gambar.setText(fasilitas.gambar or "")
            idx = self._input_status.findData(fasilitas.status)
            if idx >= 0:
                self._input_status.setCurrentIndex(idx)

        layout.addRow("Nama Fasilitas *", self._input_nama)
        layout.addRow("Harga per Jam *", self._input_harga)
        layout.addRow("Deskripsi", self._input_deskripsi)
        layout.addRow("Nama File Gambar", self._input_gambar)
        layout.addRow("", QLabel("Simpan file gambar di folder /img/"))
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
            "gambar": self._input_gambar.text().strip(),
            "status": self._input_status.currentData(),
        }
