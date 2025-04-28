import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen
from PySide6.QtCore import Qt, QPoint, QRect, QSize # Додаємо QSize


# Припускаємо, що клас Ui_ColorModelWindow з graph.py вже існує
try:
    from graph import Ui_ColorModelWindow
except ImportError:
    print("Помилка: Не вдалося імпортувати Ui_ColorModelWindow з graph.py")
    print("Переконайтеся, що файл graph.py існує і містить клас Ui_ColorModelWindow.")
    sys.exit(1)


class ColorModelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ColorModelWindow()
        self.ui.setupUi(self)

        self.image = None
        self.modified_image = None
        self.original_lab_image = None
        self.selection_start = None
        self.selection_end = None
        self.drawing = False
        self.original_pixmap = None

        self.ui.image_label.setMouseTracking(True)
        self.ui.modified_label.setMouseTracking(True)

        self.setup_events()

        self.ui.load_button.clicked.connect(self.load_image)
        self.ui.convert_to_lab_button.clicked.connect(self.convert_rgb_to_lab)
        self.ui.convert_to_rgb_button.clicked.connect(self.convert_lab_to_rgb)
        self.ui.modify_magenta_saturation_button.clicked.connect(self.modify_magenta_saturation)
        self.ui.modify_selection_saturation_button.clicked.connect(self.modify_selection_saturation)
        self.ui.compare_images_button.clicked.connect(self.compare_images)
        self.ui.reset_button.clicked.connect(self.reset_changes)
        self.ui.save_button.clicked.connect(self.save_image)

        self.ui.saturation_slider.valueChanged.connect(self.update_saturation_label)
        self.ui.brightness_slider.valueChanged.connect(self.update_brightness_label)
        self.ui.brightness_slider.valueChanged.connect(self.modify_brightness)

        self.update_button_states(False)

    def setup_events(self):
        self.ui.image_label.mouseMoveEvent = self.image_label_mouseMoveEvent
        self.ui.image_label.mousePressEvent = self.image_label_mousePressEvent
        self.ui.image_label.mouseReleaseEvent = self.image_label_mouseReleaseEvent
        self.ui.modified_label.mouseMoveEvent = self.modified_label_mouseMoveEvent

    def get_pixmap_offset_and_coords(self, label, event_pos: QPoint) -> tuple[QPoint | None, QPoint | None]:
        pixmap = label.pixmap()
        if pixmap is None or pixmap.isNull():
            return None, None

        label_size = label.size()
        pixmap_size = pixmap.size()

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2
        offset = QPoint(int(offset_x), int(offset_y))

        pixmap_coords = event_pos - offset

        return offset, pixmap_coords

    def clamp_coords_to_pixmap(self, coords: QPoint, pixmap: QPixmap) -> QPoint:
        if pixmap is None or pixmap.isNull():
            return coords

        clamped_x = max(0, min(coords.x(), pixmap.width() - 1))
        clamped_y = max(0, min(coords.y(), pixmap.height() - 1))
        return QPoint(clamped_x, clamped_y)

    def image_label_mouseMoveEvent(self, event):
        label = self.ui.image_label
        current_pixmap = label.pixmap()

        if self.image is not None and current_pixmap:
            self.show_pixel_info(event, label, self.image)

        if self.drawing and self.original_pixmap and self.selection_start:
            label_pos = event.position().toPoint()
            offset, pixmap_pos = self.get_pixmap_offset_and_coords(label, label_pos)

            if pixmap_pos is not None:
                self.selection_end = self.clamp_coords_to_pixmap(pixmap_pos, self.original_pixmap)

                temp_pixmap = self.original_pixmap.copy()
                painter = QPainter(temp_pixmap)
                pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)

                selection_rect = QRect(self.selection_start, self.selection_end).normalized()
                painter.drawRect(selection_rect)
                painter.end()

                label.setPixmap(temp_pixmap)

                self.ui.selection_info.setText(
                     f"Вибір (pix): ({self.selection_start.x()}, {self.selection_start.y()}) → ({self.selection_end.x()}, {self.selection_end.y()})"
                )

    def modified_label_mouseMoveEvent(self, event):
        if self.modified_image is not None and self.ui.modified_label.pixmap():
            self.show_pixel_info(event, self.ui.modified_label, self.modified_image)

    def image_label_mousePressEvent(self, event):
        label = self.ui.image_label
        current_pixmap = label.pixmap()

        if self.image is not None and event.button() == Qt.MouseButton.LeftButton and current_pixmap:
            label_pos = event.position().toPoint()
            offset, pixmap_pos = self.get_pixmap_offset_and_coords(label, label_pos)

            if pixmap_pos is not None:
                if 0 <= pixmap_pos.x() < current_pixmap.width() and 0 <= pixmap_pos.y() < current_pixmap.height():
                    self.selection_start = pixmap_pos
                    self.drawing = True
                    self.original_pixmap = current_pixmap.copy()
                    self.ui.info_text.append(f"Початок вибору (pix): ({self.selection_start.x()}, {self.selection_start.y()})")
                    self.selection_end = None
                    self.ui.selection_info.setText(f"Вибір (pix): ({self.selection_start.x()}, {self.selection_start.y()}) → ...")
                    self.ui.modify_selection_saturation_button.setEnabled(False)
                else:
                    self.drawing = False
                    self.selection_start = None

    def image_label_mouseReleaseEvent(self, event):
        label = self.ui.image_label
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            if self.original_pixmap:
                label.setPixmap(self.original_pixmap)

            label_pos = event.position().toPoint()
            offset, pixmap_pos = self.get_pixmap_offset_and_coords(label, label_pos)

            if pixmap_pos is not None and self.selection_start is not None:
                self.selection_end = self.clamp_coords_to_pixmap(pixmap_pos, self.original_pixmap)
            else:
                self.selection_end = None

            self.drawing = False

            if self.selection_start and self.selection_end and \
               abs(self.selection_start.x() - self.selection_end.x()) > 1 and \
               abs(self.selection_start.y() - self.selection_end.y()) > 1 and \
               self.original_pixmap:
                x1_pix, y1_pix = self.selection_start.x(), self.selection_start.y()
                x2_pix, y2_pix = self.selection_end.x(), self.selection_end.y()

                scale_x = self.image.shape[1] / self.original_pixmap.width()
                scale_y = self.image.shape[0] / self.original_pixmap.height()

                x1_img = int(min(x1_pix, x2_pix) * scale_x)
                y1_img = int(min(y1_pix, y2_pix) * scale_y)
                x2_img = int(max(x1_pix, x2_pix) * scale_x)
                y2_img = int(max(y1_pix, y2_pix) * scale_y)

                x1_img = max(0, x1_img); y1_img = max(0, y1_img)
                x2_img = min(self.image.shape[1], x2_img); y2_img = min(self.image.shape[0], y2_img)

                self.ui.selection_info.setText(
                    f"Вибрано (pix): ({x1_pix}, {y1_pix}) → ({x2_pix}, {y2_pix})\n"
                    f"Вибрано (зобр.): ({x1_img}, {y1_img}) → ({x2_img}, {y2_img})"
                )
                self.ui.info_text.append(f"Завершено вибір області на зображенні: ({x1_img}, {y1_img}) → ({x2_img}, {y2_img})")
                self.update_button_states(True)
            else:
                self.ui.selection_info.setText("Немає вибраної області (недостатній розмір)")
                self.ui.info_text.append("Вибір області скасовано (недостатній розмір)")
                self.selection_start = None
                self.selection_end = None
                self.update_button_states(True)

    def update_button_states(self, has_image):
        has_valid_selection = has_image and \
                              self.selection_start is not None and \
                              self.selection_end is not None and \
                              abs(self.selection_start.x() - self.selection_end.x()) > 1 and \
                              abs(self.selection_start.y() - self.selection_end.y()) > 1
        self.ui.modify_selection_saturation_button.setEnabled(has_valid_selection)

        # ... (решта логіки) ...
        self.ui.compare_images_button.setEnabled(has_image and self.modified_image is not None)
        self.ui.reset_button.setEnabled(has_image)
        self.ui.save_button.setEnabled(has_image and self.modified_image is not None)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Виберіть зображення", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif)"
        )

        if file_path:
            try:
                img = cv2.imread(file_path)
                if img is None:
                    raise Exception("Неможливо завантажити зображення")
                self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.modified_image = self.image.copy()
                self.original_lab_image = None

                self.display_image(self.image, self.ui.image_label)
                self.display_image(self.image, self.ui.modified_label)
                self.display_image(self.image, self.ui.compare_original)
                self.display_image(self.image, self.ui.compare_modified)

                self.ui.info_text.append(f"Зображення завантажено: {os.path.basename(file_path)}")
                self.ui.info_text.append(f"Розмір: {self.image.shape[1]}x{self.image.shape[0]}")

                self.selection_start = None
                self.selection_end = None
                self.ui.selection_info.setText("Немає вибраної області")
                self.ui.saturation_slider.setValue(0)
                self.ui.brightness_slider.setValue(0)

                self.update_button_states(True)
                self.ui.image_tabs.setCurrentIndex(0)

            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Неможливо завантажити зображення: {e}")
                self.update_button_states(False)
                self.original_pixmap = None

    def display_image(self, image_data, label):
        original_pixmap_needs_update = (label == self.ui.image_label)

        if image_data is None:
            label.setText("Немає зображення")
            label.setPixmap(QPixmap())
            if original_pixmap_needs_update:
                self.original_pixmap = None
            return
        try:
            if image_data.dtype != np.uint8:
                 if np.issubdtype(image_data.dtype, np.floating):
                     image_data = np.clip(image_data, 0, 255).astype(np.uint8)
                 elif np.issubdtype(image_data.dtype, np.integer):
                      image_data = np.clip(image_data, 0, 255).astype(np.uint8)
                 else:
                      raise ValueError(f"Непідтримуваний тип даних зображення: {image_data.dtype}")

            h, w, ch = image_data.shape
            if ch == 3:
                bytes_per_line = 3 * w
                q_image = QImage(image_data.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            else:
                raise ValueError(f"Непідтримувана кількість каналів: {ch}")

            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if original_pixmap_needs_update:
                self.original_pixmap = scaled_pixmap.copy()

        except Exception as e:
            print(f"Помилка відображення зображення: {e}")
            label.setText("Помилка відображення")
            label.setPixmap(QPixmap())
            if original_pixmap_needs_update:
                self.original_pixmap = None

    def show_pixel_info(self, event, label, source_image):
        current_pixmap = label.pixmap()
        if source_image is None or current_pixmap is None or current_pixmap.isNull():
            return

        label_pos_f = event.position()
        label_pos = label_pos_f.toPoint()

        pixmap_rect = current_pixmap.rect()
        pixmap_rect.moveCenter(label.rect().center())

        if not pixmap_rect.contains(label_pos):
             self.ui.rgb_label.setText("RGB: -")
             self.ui.lab_label.setText("Lab: -")
             self.ui.pos_label.setText("Позиція: -")
             self.ui.pixel_color_preview.setStyleSheet("background-color: none;")
             return

        pixmap_x = label_pos.x() - pixmap_rect.left()
        pixmap_y = label_pos.y() - pixmap_rect.top()

        if not (0 <= pixmap_x < current_pixmap.width() and 0 <= pixmap_y < current_pixmap.height()):
             self.ui.rgb_label.setText("RGB: - (поза pixmap)")
             self.ui.lab_label.setText("Lab: -")
             self.ui.pos_label.setText("Позиція: -")
             self.ui.pixel_color_preview.setStyleSheet("background-color: none;")
             return

        scale_x = source_image.shape[1] / current_pixmap.width()
        scale_y = source_image.shape[0] / current_pixmap.height()

        img_x = int(pixmap_x * scale_x)
        img_y = int(pixmap_y * scale_y)

        if 0 <= img_x < source_image.shape[1] and 0 <= img_y < source_image.shape[0]:
            try:
                r, g, b = source_image[img_y, img_x]
                lab_pixel = cv2.cvtColor(np.array([[[r, g, b]]], dtype=np.uint8), cv2.COLOR_RGB2Lab)[0, 0]
                l_val = lab_pixel[0] * 100 / 255.0
                a_val = int(lab_pixel[1]) - 128
                b_val = int(lab_pixel[2]) - 128

                self.ui.rgb_label.setText(f"RGB: ({r}, {g}, {b})")
                self.ui.lab_label.setText(f"Lab: ({l_val:.1f}, {a_val}, {b_val})")
                self.ui.pos_label.setText(f"Позиція: ({img_x}, {img_y})")
                self.ui.pixel_color_preview.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b}); border: 1px solid #ccc;"
                )
            except Exception as e:
                 print(f"Помилка отримання інформації про піксель: {e}")
                 self.ui.rgb_label.setText("RGB: помилка")
                 self.ui.lab_label.setText("Lab: помилка")
                 self.ui.pos_label.setText(f"Позиція: ({img_x}, {img_y})")
                 self.ui.pixel_color_preview.setStyleSheet("background-color: red;")
        else:
            self.ui.rgb_label.setText("RGB: поза межами")
            self.ui.lab_label.setText("Lab: -")
            self.ui.pos_label.setText(f"Позиція: ({img_x}, {img_y})")
            self.ui.pixel_color_preview.setStyleSheet("background-color: none;")

    def modify_selection_saturation(self):
        if self.image is None or self.selection_start is None or self.selection_end is None:
            QMessageBox.warning(self, "Увага", "Будь ласка, завантажте зображення та виділіть область.")
            return

        # Масштабування координат із QLabel у розміри оригіналу
        x1, y1 = self.selection_start.x(), self.selection_start.y()
        x2, y2 = self.selection_end.x(), self.selection_end.y()
        scale_x = self.image.shape[1] / self.original_pixmap.width()
        scale_y = self.image.shape[0] / self.original_pixmap.height()
        xa, ya = int(min(x1, x2) * scale_x), int(min(y1, y2) * scale_y)
        xb, yb = int(max(x1, x2) * scale_x), int(max(y1, y2) * scale_y)

        # Створюємо булеву маску вибраної області
        mask = np.zeros(self.image.shape[:2], dtype=bool)
        mask[ya:yb, xa:xb] = True

        factor = 1.0 + self.ui.saturation_slider.value() / 100.0
        lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
        modified_lab, cnt = self._apply_saturation_modification(lab, factor, mask)

        # Оновлюємо зображення на екрані
        self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
        self.original_lab_image = modified_lab
        self.display_image(self.modified_image, self.ui.modified_label)
        self.display_image(self.modified_image, self.ui.compare_modified)

        self.ui.info_text.append(
            f"Насиченість у вибраній області ({xa},{ya}→{xb},{yb}) змінена для {cnt} пікселів."
        )
        self.update_button_states(True)

    def reset_changes(self):
        if self.image is None:
            return
        self.modified_image = self.image.copy()
        self.original_lab_image = None
        self.selection_start = None
        self.selection_end = None

        self.display_image(self.image, self.ui.image_label)
        self.display_image(self.image, self.ui.modified_label)
        self.display_image(self.image, self.ui.compare_modified)

        self.ui.image_tabs.setCurrentIndex(0)
        self.ui.saturation_slider.setValue(0)
        self.ui.brightness_slider.setValue(0)
        self.ui.selection_info.setText("Немає вибраної області")
        self.ui.info_text.append("Всі зміни скасовано, зображення скинуто до оригіналу.")
        self.update_button_states(True)

    def _apply_saturation_modification(self, lab_image, factor, mask=None):
        l, a, b = cv2.split(lab_image)
        a_s = a.astype(np.int16) - 128
        b_s = b.astype(np.int16) - 128

        if mask is None:
            mask = np.ones_like(l, dtype=bool)

        # Вираховуємо поточну хроматичність та напрямок (кут)
        chroma = np.sqrt(a_s[mask].astype(np.float32) ** 2 + b_s[mask].astype(np.float32) ** 2)
        angles = np.arctan2(b_s[mask], a_s[mask])
        angles[chroma < 1e-6] = 0

        # Змінюємо хроматичність за вказаним фактором
        new_chroma = np.clip(chroma * factor, 0, 180)
        new_a = np.clip(new_chroma * np.cos(angles), -128, 127).astype(np.int16)
        new_b = np.clip(new_chroma * np.sin(angles), -128, 127).astype(np.int16)

        # Повертаємо зведені канали в діапазон [0,255]
        a_mod = np.clip(a_s + 128, 0, 255).astype(np.uint8)
        b_mod = np.clip(b_s + 128, 0, 255).astype(np.uint8)
        a_mod[mask] = (new_a + 128).astype(np.uint8)
        b_mod[mask] = (new_b + 128).astype(np.uint8)

        modified_lab = cv2.merge([l, a_mod, b_mod])
        return modified_lab, int(np.sum(mask))

    def modify_magenta_saturation(self):
        if self.image is None:
            return

        lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
        l, a, b = cv2.split(lab)
        a_s = a.astype(np.int16) - 128
        b_s = b.astype(np.int16) - 128

        # Визначаємо пурпурні пікселі за каналами a та b
        magenta_mask = (a_s > 15) & (b_s < -10)
        chroma = np.sqrt(a_s.astype(np.float32)**2 + b_s.astype(np.float32)**2)
        mask = magenta_mask & (chroma > 20)

        factor = 1.0 + self.ui.saturation_slider.value() / 100.0
        modified_lab, cnt = self._apply_saturation_modification(lab, factor, mask)

        self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
        self.original_lab_image = modified_lab
        self.display_image(self.modified_image, self.ui.modified_label)
        self.display_image(self.modified_image, self.ui.compare_modified)

        self.ui.info_text.append(f"Змінено насиченість {cnt} пурпурних пікселів (фактор {factor:.2f}).")
        self.update_button_states(True)

    def modify_brightness(self):
        if self.image is None:
            return
        try:
            lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
            delta = self.ui.brightness_slider.value()
            l, a, b = cv2.split(lab)
            l_mod = l.astype(np.int16) + delta
            l_mod_clipped = np.clip(l_mod, 0, 255).astype(np.uint8)
            modified_lab = cv2.merge([l_mod_clipped, a, b])

            self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
            self.original_lab_image = modified_lab # Зберігаємо результат Lab

            self.display_image(self.modified_image, self.ui.modified_label)
            self.display_image(self.modified_image, self.ui.compare_modified)
            self.ui.info_text.append(f"Яскравість (L канал) змінена на {delta}")
            self.update_button_states(True)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка зміни яскравості: {e}")

    def convert_rgb_to_lab(self):
        if self.image is None:
            return
        try:
            lab_cv = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
            self.original_lab_image = lab_cv.copy()
            self.modified_image = lab_cv

            self.display_image(self.modified_image, self.ui.modified_label)
            self.display_image(self.modified_image, self.ui.compare_modified)

            self.ui.image_tabs.setCurrentIndex(1)
            self.ui.info_text.append("Перетворення RGB → Lab виконано.")
            self.ui.info_text.append("На вкладці 'Модифіковане' відображено канали L, a, b як R, G, B.")
            self.update_button_states(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка перетворення RGB → Lab: {e}")

    def convert_lab_to_rgb(self):
        if self.original_lab_image is None:
            QMessageBox.warning(self, "Увага", "Спочатку потрібно виконати перетворення RGB → Lab.")
            return
        try:
            rgb = cv2.cvtColor(self.original_lab_image, cv2.COLOR_Lab2RGB)
            self.modified_image = rgb
            self.display_image(rgb, self.ui.modified_label)
            self.display_image(rgb, self.ui.compare_modified)
            self.ui.image_tabs.setCurrentIndex(1)
            self.ui.info_text.append("Перетворення Lab → RGB виконано.")
            self.update_button_states(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка перетворення Lab → RGB: {e}")

    def compare_images(self):
        if self.image is None or self.modified_image is None:
             QMessageBox.warning(self, "Увага", "Потрібно завантажити та модифікувати зображення для порівняння.")
             return

        if self.image.shape != self.modified_image.shape:
             QMessageBox.warning(self, "Увага", "Розміри оригінального та модифікованого зображень не співпадають. Порівняння неможливе.")
             return

        self.display_image(self.image, self.ui.compare_original)
        self.display_image(self.modified_image, self.ui.compare_modified)
        self.ui.image_tabs.setCurrentIndex(2)

        try:
            diff = cv2.absdiff(self.image, self.modified_image)
            mean_diff = np.mean(diff)
            max_diff = np.max(diff)

            self.ui.info_text.append(f"Порівняння:")
            self.ui.info_text.append(f"  Середня абсолютна різниця на піксель: {mean_diff:.2f}")
            self.ui.info_text.append(f"  Максимальна абсолютна різниця: {max_diff}")

            if mean_diff < 1:
                self.ui.info_text.append("  Візуальна різниця мінімальна або відсутня.")
            elif mean_diff < 10:
                self.ui.info_text.append("  Присутня незначна візуальна різниця.")
            else:
                self.ui.info_text.append("  Присутня помітна візуальна різниця.")

        except Exception as e:
             QMessageBox.critical(self, "Помилка", f"Помилка при розрахунку різниці зображень: {e}")
             self.ui.info_text.append("Помилка порівняння зображень.")

    def save_image(self):
        if self.modified_image is None:
            QMessageBox.warning(self, "Увага", "Немає модифікованого зображення для збереження.")
            return
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Зберегти модифіковане зображення", "modified_image.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;TIFF (*.tif *.tiff)"
        )
        if path:
            try:
                save_bgr = cv2.cvtColor(self.modified_image, cv2.COLOR_RGB2BGR)
                params = []
                if selected_filter.lower().endswith(('.jpg', '.jpeg')):
                    params = [cv2.IMWRITE_JPEG_QUALITY, 95]
                elif selected_filter.lower().endswith('.png'):
                     params = [cv2.IMWRITE_PNG_COMPRESSION, 3]

                success = cv2.imwrite(path, save_bgr, params)

                if success:
                    self.ui.info_text.append(f"Зображення успішно збережено як: {os.path.basename(path)}")
                else:
                     raise Exception("cv2.imwrite повернув False")

            except Exception as e:
                QMessageBox.critical(self, "Помилка збереження", f"Не вдалося зберегти зображення:\n{e}")

    def update_saturation_label(self, value=None):
        val = self.ui.saturation_slider.value()
        factor = 1.0 + val / 100.0
        text = f"Насиченість: {val:+d}% ({factor:.2f}x)"
        self.ui.saturation_label.setText(text)

    def update_brightness_label(self, value=None):
        val = self.ui.brightness_slider.value()
        text = f"Яскравість (L): {val:+d}"
        self.ui.brightness_label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ColorModelApp()
    win.setMinimumSize(1200, 700)
    win.show()
    sys.exit(app.exec())
