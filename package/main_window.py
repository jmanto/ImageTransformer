import glob
import os.path

from PyQt6 import QtWidgets, QtCore, QtGui

from package.image import CustomImage
import package.app_base as ab


class Worker(QtCore.QObject):
    QtCore.Signal = QtCore.pyqtSignal
    image_converted = QtCore.Signal(object, bool)
    finished = QtCore.Signal()

    def __init__(self, images_to_convert, mode, quality, size, max_size, max_ratio, folder):
        super().__init__()

        self.images_to_convert = images_to_convert
        self.mode = mode
        self.quality = quality
        self.size = size
        self.max_size = max_size
        self.max_ratio = max_ratio
        self.folder = folder
        self.runs = True

    def convert_images(self):
        for image_lw_item in self.images_to_convert:
            if self.runs and not image_lw_item.processed:
                image = CustomImage(path=image_lw_item.text(), folder=self.folder)
                success = image.reduce_image(mode=self.mode, ratio=self.size, quality=self.quality, max_size=self.max_size, max_ratio=self.max_ratio)
                self.image_converted.emit(image_lw_item, success)

        self.finished.emit()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.window_maximized = False

        self.setWindowTitle("ImageTransformer")
        self.setWindowIcon(QtGui.QIcon('assets/ImageTransformer.png'))
        x, y = ab.window_corner(ab.width, ab.height)
        self.setGeometry(x, y, ab.width, ab.height)

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_quality = QtWidgets.QLabel("Quality:")
        self.spn_quality = QtWidgets.QSpinBox()
        self.lbl_size = QtWidgets.QLabel("Ratio:")
        self.spn_size = QtWidgets.QSpinBox()
        self.lbl_target = QtWidgets.QLabel("Target size:")
        self.le_target = QtWidgets.QLineEdit()
        self.lbl_dossierOut = QtWidgets.QLabel("Output folder:")
        self.le_dossierOut = QtWidgets.QLineEdit()
        self.lw_files = QtWidgets.QListWidget()
        self.btn_convert = QtWidgets.QPushButton("Conversion")
        self.lbl_dropInfo = QtWidgets.QLabel("^ Drop the images onto the interface")

    def modify_widgets(self):
        style = ab.apply_style()
        self.setStyleSheet(style)

        # Alignment
        self.spn_quality.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.spn_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.le_target.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.le_dossierOut.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Range
        self.spn_quality.setRange(1, 100)
        self.spn_quality.setValue(75)
        self.spn_size.setRange(1, 100)
        self.spn_size.setValue(50)

        # Divers
        self.le_dossierOut.setPlaceholderText("Output folder ...")
        self.le_target.setPlaceholderText("1920, 1080, 1")
        self.le_dossierOut.setText("reduced")
        self.lbl_dropInfo.setVisible(False)

        self.setAcceptDrops(True)
        self.lw_files.setAlternatingRowColors(True)
        self.lw_files.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_quality, 0, 0, 1, 1)
        self.main_layout.addWidget(self.spn_quality, 0, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_size, 1, 0, 1, 1)
        self.main_layout.addWidget(self.spn_size, 1, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_target, 2, 0, 1, 1)
        self.main_layout.addWidget(self.le_target, 2, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_dossierOut, 3, 0, 1, 1)
        self.main_layout.addWidget(self.le_dossierOut, 3, 1, 1, 1)
        self.main_layout.addWidget(self.lw_files, 4, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_dropInfo, 5, 0, 1, 2)
        self.main_layout.addWidget(self.btn_convert, 6, 0, 1, 2)

    def setup_connections(self):
        QtGui.QShortcut(QtGui.QKeySequence("Backspace"), self.lw_files, self.delete_selected_items)
        QtGui.QShortcut(QtGui.QKeySequence("F"), self, self.change_window_state)

        self.btn_convert.clicked.connect(self.convert_images)

    def change_window_state(self):
        self.window_maximized = not self.window_maximized

        if self.window_maximized:
            self.showFullScreen()
        else:
            self.showNormal()

    def convert_images(self):
        quality = self.spn_quality.value()
        size = self.spn_size.value() / 100.0
        if self.le_target.text():
            max_dim = self.le_target.text().split(", ")
            if len(max_dim) == 3:

                dim1, dim2 = int(max_dim[0]), int(max_dim[1])
                max_size = (max(dim1, dim2), min(dim1, dim2))
                max_ratio = float(max_dim[2])
                mode = "target"
            else:
                msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                                "Size error",
                                                "The format of the field 'Target size' must be: dim1, dim2, max_ratio"
                                                "'Ratio' mode is activated.")
                msg_box.exec_()

                max_size = (1, 1)
                max_ratio = 1
                mode = "ratio"
        else:
            max_size = (1, 1)
            max_ratio = 1
            mode = "ratio"

        folder = self.le_dossierOut.text()

        lw_items = [self.lw_files.item(index) for index in range(self.lw_files.count())]
        images_a_convertir = [1 for lw_item in lw_items if not lw_item.processed]
        if not images_a_convertir:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                            "No image to convert",
                                            "All images have been converted.")
            msg_box.exec_()
            return False

        self.thread = QtCore.QThread(self)

        self.worker = Worker(images_to_convert=lw_items,
                             mode=mode,
                             quality=quality,
                             size=size,
                             max_size=max_size,
                             max_ratio=max_ratio,
                             folder=folder)

        self.worker.moveToThread(self.thread)
        self.worker.image_converted.connect(self.image_converted)
        self.thread.started.connect(self.worker.convert_images)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

        self.prg_dialog = QtWidgets.QProgressDialog(f"Converting {len(images_a_convertir)} image(s)", "Abort", 1, len(images_a_convertir))
        self.prg_dialog.canceled.connect(self.abort)
        self.prg_dialog.show()

    def abort(self):
        self.worker.runs = False
        self.thread.quit()

    def image_converted(self, lw_item, success):
        if success:
            lw_item.setIcon(QtGui.QIcon("assets/checked.png"))
            lw_item.processed = True
            self.prg_dialog.setValue(self.prg_dialog.value() + 1)

    def delete_selected_items(self):
        for lw_item in self.lw_files.selectedItems():
            row = self.lw_files.row(lw_item)
            self.lw_files.takeItem(row)

    def dragEnterEvent(self, event):
        self.lbl_dropInfo.setVisible(True)
        event.accept()

    def dragLeaveEvent(self, event):
        self.lbl_dropInfo.setVisible(False)

    def dropEvent(self, event):
        event.accept()
        for url in event.mimeData().urls():
            if os.path.isfile(url.toLocalFile()):
                self.add_file(path=url.toLocalFile())
            else:
                children = glob.iglob(url.toLocalFile() + r"/**/*.*", recursive=True)
                children_image = [f for f in children if ".jpeg" in f or ".jpg" in f]

                for image_path in children_image:
                    self.add_file(path=image_path)

        self.lbl_dropInfo.setVisible(False)

    def add_file(self, path):
        items = [self.lw_files.item(index).text() for index in range(self.lw_files.count())]

        if path not in items:
            lw_item = QtWidgets.QListWidgetItem(path)
            lw_item.setIcon(QtGui.QIcon("assets/unchecked.png"))
            lw_item.processed = False
            self.lw_files.addItem(lw_item)
