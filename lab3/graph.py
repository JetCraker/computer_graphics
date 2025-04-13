# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
                               QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QSizePolicy, QSpinBox,
                               QTabWidget, QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 900)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")

        # Sinh Fractal Tab
        self.tab_sinh = QWidget()
        self.tab_sinh.setObjectName(u"tab_sinh")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_sinh)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        # Left panel for sinh fractal (canvas will be added in main code)
        self.sinh_left_panel = QWidget(self.tab_sinh)
        self.sinh_left_panel.setObjectName(u"sinh_left_panel")
        self.sinh_left_layout = QVBoxLayout(self.sinh_left_panel)
        self.sinh_left_layout.setObjectName(u"sinh_left_layout")

        self.horizontalLayout_2.addWidget(self.sinh_left_panel, 4)

        # Right control panel for sinh fractal
        self.sinh_control_panel = QWidget(self.tab_sinh)
        self.sinh_control_panel.setObjectName(u"sinh_control_panel")
        self.sinh_control_layout = QVBoxLayout(self.sinh_control_panel)
        self.sinh_control_layout.setObjectName(u"sinh_control_layout")

        # Parameter group for sinh fractal
        self.sinh_param_group = QGroupBox(self.sinh_control_panel)
        self.sinh_param_group.setObjectName(u"sinh_param_group")
        self.sinh_param_layout = QFormLayout(self.sinh_param_group)
        self.sinh_param_layout.setObjectName(u"sinh_param_layout")

        # C value inputs
        self.c_real_input = QDoubleSpinBox(self.sinh_param_group)
        self.c_real_input.setObjectName(u"c_real_input")
        self.c_real_input.setRange(-10, 10)
        self.c_real_input.setSingleStep(0.1)
        self.c_real_input.setValue(0.0)
        self.sinh_param_layout.addRow(u"Константа c (дійсна частина):", self.c_real_input)

        self.c_imag_input = QDoubleSpinBox(self.sinh_param_group)
        self.c_imag_input.setObjectName(u"c_imag_input")
        self.c_imag_input.setRange(-10, 10)
        self.c_imag_input.setSingleStep(0.1)
        self.c_imag_input.setValue(0.0)
        self.sinh_param_layout.addRow(u"Константа c (уявна частина):", self.c_imag_input)

        # Iterations and escape radius
        self.max_iterations_input = QSpinBox(self.sinh_param_group)
        self.max_iterations_input.setObjectName(u"max_iterations_input")
        self.max_iterations_input.setRange(10, 1000)
        self.max_iterations_input.setSingleStep(10)
        self.max_iterations_input.setValue(100)
        self.sinh_param_layout.addRow(u"Максимальна кількість ітерацій:", self.max_iterations_input)

        self.escape_radius_input = QDoubleSpinBox(self.sinh_param_group)
        self.escape_radius_input.setObjectName(u"escape_radius_input")
        self.escape_radius_input.setRange(2, 10000)
        self.escape_radius_input.setSingleStep(10)
        self.escape_radius_input.setValue(1000)
        self.sinh_param_layout.addRow(u"Радіус виходу:", self.escape_radius_input)

        # Resolution inputs
        self.width_input = QSpinBox(self.sinh_param_group)
        self.width_input.setObjectName(u"width_input")
        self.width_input.setRange(100, 4000)
        self.width_input.setSingleStep(100)
        self.width_input.setValue(800)
        self.sinh_param_layout.addRow(u"Ширина (пікселі):", self.width_input)

        self.height_input = QSpinBox(self.sinh_param_group)
        self.height_input.setObjectName(u"height_input")
        self.height_input.setRange(100, 4000)
        self.height_input.setSingleStep(100)
        self.height_input.setValue(600)
        self.sinh_param_layout.addRow(u"Висота (пікселі):", self.height_input)

        # Adaptive resolution option
        self.adaptive_resolution = QCheckBox(self.sinh_param_group)
        self.adaptive_resolution.setObjectName(u"adaptive_resolution")
        self.adaptive_resolution.setChecked(True)
        self.sinh_param_layout.addRow(u"", self.adaptive_resolution)

        # Colormap selection
        self.colormap_combo = QComboBox(self.sinh_param_group)
        self.colormap_combo.setObjectName(u"colormap_combo")
        colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'hot', 'cool', 'jet']
        self.colormap_combo.addItems(colormaps)
        self.sinh_param_layout.addRow(u"Колірна схема:", self.colormap_combo)

        # Coordinates label
        self.coords_label = QLabel(self.sinh_param_group)
        self.coords_label.setObjectName(u"coords_label")
        self.sinh_param_layout.addRow(u"Координати курсору:", self.coords_label)

        self.sinh_control_layout.addWidget(self.sinh_param_group)

        # View control group
        self.sinh_view_group = QGroupBox(self.sinh_control_panel)
        self.sinh_view_group.setObjectName(u"sinh_view_group")
        self.sinh_view_layout = QVBoxLayout(self.sinh_view_group)
        self.sinh_view_layout.setObjectName(u"sinh_view_layout")

        # Clear scene button
        self.sinh_clear_btn = QPushButton(self.sinh_view_group)
        self.sinh_clear_btn.setObjectName(u"sinh_clear_btn")
        self.sinh_view_layout.addWidget(self.sinh_clear_btn)

        self.sinh_control_layout.addWidget(self.sinh_view_group)

        # Generate and save buttons
        self.sinh_generate_btn = QPushButton(self.sinh_control_panel)
        self.sinh_generate_btn.setObjectName(u"sinh_generate_btn")
        self.sinh_control_layout.addWidget(self.sinh_generate_btn)

        self.sinh_save_btn = QPushButton(self.sinh_control_panel)
        self.sinh_save_btn.setObjectName(u"sinh_save_btn")
        self.sinh_control_layout.addWidget(self.sinh_save_btn)

        self.sinh_control_layout.addStretch()

        self.horizontalLayout_2.addWidget(self.sinh_control_panel, 1)

        self.tabWidget.addTab(self.tab_sinh, "")

        # Hilbert Curve Tab
        self.tab_hilbert = QWidget()
        self.tab_hilbert.setObjectName(u"tab_hilbert")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_hilbert)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        # Left panel for hilbert curve (canvas will be added in main code)
        self.hilbert_left_panel = QWidget(self.tab_hilbert)
        self.hilbert_left_panel.setObjectName(u"hilbert_left_panel")
        self.hilbert_left_layout = QVBoxLayout(self.hilbert_left_panel)
        self.hilbert_left_layout.setObjectName(u"hilbert_left_layout")

        self.horizontalLayout_3.addWidget(self.hilbert_left_panel, 4)

        # Right control panel for hilbert curve
        self.hilbert_control_panel = QWidget(self.tab_hilbert)
        self.hilbert_control_panel.setObjectName(u"hilbert_control_panel")
        self.hilbert_control_layout = QVBoxLayout(self.hilbert_control_panel)
        self.hilbert_control_layout.setObjectName(u"hilbert_control_layout")

        # Parameter group for hilbert curve
        self.hilbert_param_group = QGroupBox(self.hilbert_control_panel)
        self.hilbert_param_group.setObjectName(u"hilbert_param_group")
        self.hilbert_param_layout = QFormLayout(self.hilbert_param_group)
        self.hilbert_param_layout.setObjectName(u"hilbert_param_layout")

        # Iterations input
        self.hilbert_iterations_input = QSpinBox(self.hilbert_param_group)
        self.hilbert_iterations_input.setObjectName(u"hilbert_iterations_input")
        self.hilbert_iterations_input.setRange(1, 8)
        self.hilbert_iterations_input.setValue(5)
        self.hilbert_param_layout.addRow(u"Кількість ітерацій:", self.hilbert_iterations_input)

        # Line width input
        self.line_width_input = QDoubleSpinBox(self.hilbert_param_group)
        self.line_width_input.setObjectName(u"line_width_input")
        self.line_width_input.setRange(0.5, 5)
        self.line_width_input.setSingleStep(0.5)
        self.line_width_input.setValue(1.0)
        self.hilbert_param_layout.addRow(u"Товщина лінії:", self.line_width_input)

        # Color selection
        self.color_btn = QPushButton(self.hilbert_param_group)
        self.color_btn.setObjectName(u"color_btn")
        self.color_btn.setStyleSheet(u"background-color: blue")
        self.hilbert_param_layout.addRow(u"Колір:", self.color_btn)

        self.hilbert_control_layout.addWidget(self.hilbert_param_group)

        # Generate and save buttons
        self.hilbert_generate_btn = QPushButton(self.hilbert_control_panel)
        self.hilbert_generate_btn.setObjectName(u"hilbert_generate_btn")
        self.hilbert_control_layout.addWidget(self.hilbert_generate_btn)

        self.hilbert_save_btn = QPushButton(self.hilbert_control_panel)
        self.hilbert_save_btn.setObjectName(u"hilbert_save_btn")
        self.hilbert_control_layout.addWidget(self.hilbert_save_btn)

        self.hilbert_control_layout.addStretch()

        self.horizontalLayout_3.addWidget(self.hilbert_control_panel, 1)

        self.tabWidget.addTab(self.tab_hilbert, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Візуалізатор фракталів", None))
        self.sinh_param_group.setTitle(QCoreApplication.translate("MainWindow", u"Параметри фракталу", None))
        self.adaptive_resolution.setText(
            QCoreApplication.translate("MainWindow", u"Адаптивна роздільна здатність при збільшенні", None))
        self.coords_label.setText(QCoreApplication.translate("MainWindow", u"X: --- Y: ---", None))
        self.sinh_view_group.setTitle(QCoreApplication.translate("MainWindow", u"Керування переглядом", None))
        self.sinh_clear_btn.setText(QCoreApplication.translate("MainWindow", u"Очистити сцену", None))
        self.sinh_generate_btn.setText(QCoreApplication.translate("MainWindow", u"Згенерувати фрактал", None))
        self.sinh_save_btn.setText(QCoreApplication.translate("MainWindow", u"Зберегти зображення", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sinh),
                                  QCoreApplication.translate("MainWindow", u"Фрактал sh(z)+c", None))
        self.hilbert_param_group.setTitle(QCoreApplication.translate("MainWindow", u"Параметри кривої", None))
        self.color_btn.setText(QCoreApplication.translate("MainWindow", u"Вибрати колір", None))
        self.hilbert_generate_btn.setText(QCoreApplication.translate("MainWindow", u"Згенерувати криву", None))
        self.hilbert_save_btn.setText(QCoreApplication.translate("MainWindow", u"Зберегти зображення", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_hilbert),
                                  QCoreApplication.translate("MainWindow", u"Крива Гільберта-Пеано", None))
    # retranslateUi