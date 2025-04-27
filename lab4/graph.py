# -*- coding: utf-8 -*-

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QTextEdit, QHBoxLayout, QTabWidget, QGridLayout, QSlider,
    QGroupBox, QSplitter, QFrame, QScrollArea
)
from PySide6.QtGui import QPixmap, QImage, QColor, QFont


class Ui_ColorModelWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("ColorModelWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setWindowTitle("Досліди з моделями кольорів")

        self.centralwidget = QWidget(MainWindow)
        self.main_layout = QHBoxLayout(self.centralwidget)

        # Ліва панель - зображення і кнопки
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        # Вкладки для зображень
        self.image_tabs = QTabWidget()
        # Оригінал
        self.orig_tab = QWidget()
        self.orig_layout = QVBoxLayout(self.orig_tab)
        self.image_scroll_area = QScrollArea(); self.image_scroll_area.setWidgetResizable(True)
        self.image_container = QWidget(); self.image_container_layout = QVBoxLayout(self.image_container)
        self.image_label = QLabel("Завантажте зображення")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(600, 400))
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        self.image_container_layout.addWidget(self.image_label)
        self.image_scroll_area.setWidget(self.image_container)
        self.orig_layout.addWidget(self.image_scroll_area)
        self.image_tabs.addTab(self.orig_tab, "Оригінал")
        # Модифіковане
        self.modified_tab = QWidget()
        self.modified_layout = QVBoxLayout(self.modified_tab)
        self.modified_scroll_area = QScrollArea(); self.modified_scroll_area.setWidgetResizable(True)
        self.modified_container = QWidget(); self.modified_container_layout = QVBoxLayout(self.modified_container)
        self.modified_label = QLabel("Тут відображатиметься модифіковане зображення")
        self.modified_label.setAlignment(Qt.AlignCenter)
        self.modified_label.setMinimumSize(QSize(600, 400))
        self.modified_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        self.modified_container_layout.addWidget(self.modified_label)
        self.modified_scroll_area.setWidget(self.modified_container)
        self.modified_layout.addWidget(self.modified_scroll_area)
        self.image_tabs.addTab(self.modified_tab, "Модифіковане")
        # Порівняння
        self.compare_tab = QWidget(); self.compare_layout = QHBoxLayout(self.compare_tab)
        self.compare_original = QLabel("Оригінал"); self.compare_original.setAlignment(Qt.AlignCenter)
        self.compare_original.setStyleSheet("border: 1px solid #ccc;")
        self.compare_modified = QLabel("Модифіковане"); self.compare_modified.setAlignment(Qt.AlignCenter)
        self.compare_modified.setStyleSheet("border: 1px solid #ccc;")
        self.compare_layout.addWidget(self.compare_original)
        self.compare_layout.addWidget(self.compare_modified)
        self.image_tabs.addTab(self.compare_tab, "Порівняння")

        self.left_layout.addWidget(self.image_tabs)

        # Інформація про піксель
        self.pixel_info_group = QGroupBox("Інформація про піксель")
        self.pixel_info_layout = QGridLayout(self.pixel_info_group)
        self.rgb_label = QLabel("RGB: ")
        self.lab_label = QLabel("Lab: ")
        self.pos_label = QLabel("Позиція: ")
        self.pixel_info_layout.addWidget(self.rgb_label, 0, 0)
        self.pixel_info_layout.addWidget(self.lab_label, 1, 0)
        self.pixel_info_layout.addWidget(self.pos_label, 2, 0)
        self.pixel_color_preview = QLabel()
        self.pixel_color_preview.setMinimumSize(QSize(50, 50))
        self.pixel_color_preview.setStyleSheet("background-color: #000; border: 1px solid #ccc;")
        self.pixel_info_layout.addWidget(self.pixel_color_preview, 0, 1, 3, 1, Qt.AlignCenter)
        self.left_layout.addWidget(self.pixel_info_group)

        # Кнопки операцій
        self.buttons_group = QGroupBox("Операції з зображенням")
        self.buttons_layout = QGridLayout(self.buttons_group)
        self.load_button = QPushButton("Завантажити зображення")
        self.load_button.setMinimumHeight(35)
        self.load_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.convert_to_lab_button = QPushButton("RGB → Lab")
        self.convert_to_rgb_button = QPushButton("Lab → RGB")
        self.modify_magenta_saturation_button = QPushButton("Змінити насиченість Magenta")
        self.modify_selection_saturation_button = QPushButton("Змінити насиченість вибраної області")
        self.compare_images_button = QPushButton("Порівняти зображення")
        self.reset_button = QPushButton("Скинути зміни")
        self.save_button = QPushButton("Зберегти зображення")
        self.save_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.buttons_layout.addWidget(self.load_button, 0, 0, 1, 2)
        self.buttons_layout.addWidget(self.convert_to_lab_button, 1, 0)
        self.buttons_layout.addWidget(self.convert_to_rgb_button, 1, 1)
        self.buttons_layout.addWidget(self.modify_magenta_saturation_button, 2, 0, 1, 2)
        self.buttons_layout.addWidget(self.modify_selection_saturation_button, 3, 0, 1, 2)
        self.buttons_layout.addWidget(self.compare_images_button, 4, 0)
        self.buttons_layout.addWidget(self.reset_button, 4, 1)
        self.buttons_layout.addWidget(self.save_button, 5, 0, 1, 2)
        self.left_layout.addWidget(self.buttons_group)

        # Права панель - налаштування та журнал
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # Налаштування
        self.settings_group = QGroupBox("Налаштування")
        self.settings_layout = QVBoxLayout(self.settings_group)
        # Насиченість
        self.saturation_label = QLabel("Насиченість (saturation):")
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.setTickPosition(QSlider.TicksBelow)
        self.saturation_slider.setTickInterval(10)
        self.settings_layout.addWidget(self.saturation_label)
        self.settings_layout.addWidget(self.saturation_slider)
        # Яскравість
        self.brightness_label = QLabel("Яскравість:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(10)
        self.settings_layout.addWidget(self.brightness_label)
        self.settings_layout.addWidget(self.brightness_slider)
        self.right_layout.addWidget(self.settings_group)

        # Вибрана область
        self.selection_group = QGroupBox("Вибрана область")
        self.selection_layout = QVBoxLayout(self.selection_group)
        self.selection_info = QLabel("Немає вибраної області")
        self.selection_layout.addWidget(self.selection_info)
        self.right_layout.addWidget(self.selection_group)

        # Журнал подій
        self.log_group = QGroupBox("Журнал подій")
        self.log_layout = QVBoxLayout(self.log_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.log_layout.addWidget(self.info_text)
        self.right_layout.addWidget(self.log_group)

        # Роздільник панелей
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([800, 400])
        self.main_layout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        # Початковий журнал
        self.info_text.append("Програму запущено. Будь ласка, завантажте зображення для початку роботи.")