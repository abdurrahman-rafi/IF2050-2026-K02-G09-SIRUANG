import sys

from PyQt6.QtWidgets import QApplication

from src.controller.fasilitas_controller import FasilitasController
from src.controller.laporan_controller import LaporanController
from src.controller.notifikasi_controller import NotifikasiController
from src.controller.reservasi_controller import ReservasiController
from src.controller.warga_controller import WargaController
from src.data.database_manager import DatabaseManager
from src.data.data_repository import DataRepository
from src.service.notification_service import NotificationService
from src.view.main_window import MainWindow

# TODO: pindahkan konfigurasi database ke file .env atau config.ini
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/siruang"


def main() -> None:
    """Entry point aplikasi SIRUANG. Menginisialisasi semua layer dan menjalankan GUI."""
    app = QApplication(sys.argv)

    db_manager = DatabaseManager(DATABASE_URL)
    db_manager.buka_koneksi()

    repository = DataRepository(db_manager)
    notification_service = NotificationService()

    notifikasi_ctrl = NotifikasiController(repository, notification_service)
    warga_ctrl = WargaController(repository)
    fasilitas_ctrl = FasilitasController(repository)
    reservasi_ctrl = ReservasiController(repository, notifikasi_ctrl)
    laporan_ctrl = LaporanController(repository)

    window = MainWindow(
        warga_ctrl,
        fasilitas_ctrl,
        reservasi_ctrl,
        laporan_ctrl,
        notifikasi_ctrl,
        repository,
    )
    window.show()

    exit_code = app.exec()
    db_manager.tutup_koneksi()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
