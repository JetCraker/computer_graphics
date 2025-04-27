import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QImage, Qt
from graph import Ui_ColorModelWindow


class ColorModelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ColorModelWindow()
        self.ui.setupUi(self)

        # Змінні класу
        self.image = None
        self.modified_image = None
        self.original_lab_image = None
        self.selection_start = None
        self.selection_end = None
        self.drawing = False

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

    def image_label_mouseMoveEvent(self, event):
        if self.image is not None:
            self.show_pixel_info(event, self.ui.image_label)
            if self.drawing:
                self.selection_end = (event.position().x(), event.position().y())
                self.ui.selection_info.setText(
                    f"Вибрана область: від {self.selection_start} до {self.selection_end}"
                )

    def modified_label_mouseMoveEvent(self, event):
        if self.modified_image is not None:
            self.show_pixel_info(event, self.ui.modified_label)

    def image_label_mousePressEvent(self, event):
        if self.image is not None:
            self.selection_start = (event.position().x(), event.position().y())
            self.drawing = True
            self.ui.info_text.append(f"Початок вибору області: {self.selection_start}")

    def image_label_mouseReleaseEvent(self, event):
        if self.image is not None and self.drawing:
            self.selection_end = (event.position().x(), event.position().y())
            self.drawing = False

            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            scale_x = self.image.shape[1] / self.ui.image_label.pixmap().width()
            scale_y = self.image.shape[0] / self.ui.image_label.pixmap().height()

            x1_img = int(x1 * scale_x)
            y1_img = int(y1 * scale_y)
            x2_img = int(x2 * scale_x)
            y2_img = int(y2 * scale_y)

            self.ui.selection_info.setText(
                f"Вибрана область: від ({x1:.1f}, {y1:.1f}) до ({x2:.1f}, {y2:.1f})\n"
                f"На зображенні: від ({x1_img}, {y1_img}) до ({x2_img}, {y2_img})"
            )
            self.ui.info_text.append(f"Вибрано область на зображенні: ({x1_img}, {y1_img}) → ({x2_img}, {y2_img})")
            self.update_button_states(True)

    def update_button_states(self, has_image):
        self.ui.convert_to_lab_button.setEnabled(has_image)
        self.ui.convert_to_rgb_button.setEnabled(has_image)
        self.ui.modify_magenta_saturation_button.setEnabled(has_image)
        self.ui.saturation_slider.setEnabled(has_image)
        self.ui.brightness_slider.setEnabled(has_image)

        has_selection = has_image and self.selection_start is not None and self.selection_end is not None
        self.ui.modify_selection_saturation_button.setEnabled(has_selection)

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
                self.original_lab_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)

                self.display_image(self.image, self.ui.image_label)
                self.display_image(self.image, self.ui.modified_label)

                self.ui.info_text.append(f"Зображення завантажено: {os.path.basename(file_path)}")
                self.ui.info_text.append(f"Розмір: {self.image.shape[1]}x{self.image.shape[0]}")

                self.selection_start = None
                self.selection_end = None
                self.ui.selection_info.setText("Немає вибраної області")
                self.ui.saturation_slider.setValue(0)
                self.ui.brightness_slider.setValue(0)

                self.update_button_states(True)

            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Неможливо завантажити зображення: {e}")

    def display_image(self, image, label):
        if image is None:
            return
        h, w, _ = image.shape
        bytes_per_line = 3 * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)

    def show_pixel_info(self, event, label):
        if self.image is None or label.pixmap() is None:
            return
        scale_x = self.image.shape[1] / label.pixmap().width()
        scale_y = self.image.shape[0] / label.pixmap().height()
        x = int(event.position().x() * scale_x)
        y = int(event.position().y() * scale_y)
        if 0 <= x < self.image.shape[1] and 0 <= y < self.image.shape[0]:
            r, g, b = self.image[y, x]
            lab_pixel = cv2.cvtColor(np.array([[[r, g, b]]], dtype=np.uint8), cv2.COLOR_RGB2Lab)[0, 0]
            l_val, a_val, b_val = lab_pixel
            self.ui.rgb_label.setText(f"RGB: ({r}, {g}, {b})")
            self.ui.lab_label.setText(f"Lab: ({l_val:.1f}, {a_val:.1f}, {b_val:.1f})")
            self.ui.pos_label.setText(f"Позиція: ({x}, {y})")
            self.ui.pixel_color_preview.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); border: 1px solid #ccc;"
            )

    def convert_rgb_to_lab(self):
        if self.image is None:
            return
        try:
            lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
            norm = lab.copy().astype(np.float32)
            norm[:, :, 0] = norm[:, :, 0] * 255 / 100
            norm[:, :, 1:] += 128
            self.original_lab_image = lab
            self.modified_image = np.clip(norm, 0, 255).astype(np.uint8)
            self.display_image(self.modified_image, self.ui.modified_label)
            self.display_image(self.modified_image, self.ui.compare_modified)
            self.ui.image_tabs.setCurrentIndex(1)
            self.ui.info_text.append("Перетворення RGB → Lab виконано")
            self.update_button_states(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка перетворення RGB → Lab: {e}")

    def convert_lab_to_rgb(self):
        if self.original_lab_image is None:
            return
        try:
            rgb = cv2.cvtColor(self.original_lab_image, cv2.COLOR_Lab2RGB)
            self.modified_image = rgb
            self.display_image(rgb, self.ui.modified_label)
            self.display_image(rgb, self.ui.compare_modified)
            self.ui.image_tabs.setCurrentIndex(1)
            self.ui.info_text.append("Перетворення Lab → RGB виконано")
            self.update_button_states(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка перетворення Lab → RGB: {e}")

    def update_saturation_label(self, value=None):
        val = self.ui.saturation_slider.value()
        factor = 1.0 + val / 100.0
        text = f"Насиченість: {val:+d}% ({factor:.2f}x)"
        self.ui.saturation_label.setText(text)

    def update_brightness_label(self, value=None):
        val = self.ui.brightness_slider.value()
        text = f"Яскравість: {val:+d}"
        self.ui.brightness_label.setText(text)

    def modify_magenta_saturation(self):
        if self.image is None:
            return
        lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
        l, a, b = cv2.split(lab)
        a_s = a.astype(np.int16) - 128
        b_s = b.astype(np.int16) - 128
        magenta_mask = (a_s > 10) & (b_s < -5)
        chroma = np.sqrt(a_s.astype(np.float32)**2 + b_s.astype(np.float32)**2)
        mask = magenta_mask & (chroma > 10)
        factor = 1.0 + self.ui.saturation_slider.value() / 100.0
        if np.any(mask):
            angles = np.arctan2(b_s[mask], a_s[mask])
            curr = chroma[mask]
            new_chroma = np.clip(curr * factor, 0, 128)
            a_s[mask] = (new_chroma * np.cos(angles)).astype(np.int16)
            b_s[mask] = (new_chroma * np.sin(angles)).astype(np.int16)
        a_mod = np.clip(a_s + 128, 0, 255).astype(np.uint8)
        b_mod = np.clip(b_s + 128, 0, 255).astype(np.uint8)
        modified_lab = cv2.merge([l, a_mod, b_mod])
        self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
        self.display_image(self.modified_image, self.ui.modified_label)
        self.display_image(self.modified_image, self.ui.compare_modified)
        pixels = np.sum(mask)
        self.ui.info_text.append(f"Модифіковано {pixels} пурпурних пікселів (фактор {factor:.2f})")
        self.update_button_states(True)

    def modify_selection_saturation(self):
        if self.image is None or self.selection_start is None or self.selection_end is None:
            return
        try:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            x1, x2 = sorted((x1, x2))
            y1, y2 = sorted((y1, y2))
            sx = self.image.shape[1] / self.ui.image_label.pixmap().width()
            sy = self.image.shape[0] / self.ui.image_label.pixmap().height()
            xa, xb = int(x1*sx), int(x2*sx)
            ya, yb = int(y1*sy), int(y2*sy)
            lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
            l, a, b = cv2.split(lab)
            roi_a = a[ya:yb, xa:xb].astype(np.int16) - 128
            roi_b = b[ya:yb, xa:xb].astype(np.int16) - 128
            chroma = np.sqrt(roi_a.astype(np.float32)**2 + roi_b.astype(np.float32)**2)
            mask = chroma > 5
            factor = 1.0 + self.ui.saturation_slider.value() / 100.0
            if np.any(mask):
                angles = np.arctan2(roi_b[mask], roi_a[mask])
                curr = chroma[mask]
                new_ch = curr * factor
                roi_a[mask] = np.clip(new_ch * np.cos(angles), -128, 127).astype(np.int16)
                roi_b[mask] = np.clip(new_ch * np.sin(angles), -128, 127).astype(np.int16)
            a_mod = a.copy()
            b_mod = b.copy()
            a_mod[ya:yb, xa:xb] = np.clip(roi_a + 128, 0, 255).astype(np.uint8)
            b_mod[ya:yb, xa:xb] = np.clip(roi_b + 128, 0, 255).astype(np.uint8)
            modified_lab = cv2.merge([l, a_mod, b_mod])
            self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
            self.display_image(self.modified_image, self.ui.modified_label)
            self.display_image(self.modified_image, self.ui.compare_modified)
            pixels = np.sum(mask)
            self.ui.info_text.append(
                f"Насиченість вибраної області змінено на фактор {factor:.2f}, модифіковано {pixels} пікселів"
            )
            self.update_button_states(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка зміни насиченості: {e}")

    def modify_brightness(self):
        if self.image is None:
            return
        lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab).astype(np.int16)
        delta = self.ui.brightness_slider.value()
        lab[:, :, 0] = np.clip(lab[:, :, 0] + delta, 0, 255)
        modified_lab = lab.astype(np.uint8)
        self.modified_image = cv2.cvtColor(modified_lab, cv2.COLOR_Lab2RGB)
        self.display_image(self.modified_image, self.ui.modified_label)
        self.display_image(self.modified_image, self.ui.compare_modified)
        self.ui.info_text.append(f"Яскравість змінена на {delta}")
        self.update_button_states(True)

    def compare_images(self):
        if self.image is None or self.modified_image is None:
            return
        self.display_image(self.image, self.ui.compare_original)
        self.display_image(self.modified_image, self.ui.compare_modified)
        self.ui.image_tabs.setCurrentIndex(2)
        diff = cv2.absdiff(self.image, self.modified_image)
        m = np.mean(diff)
        self.ui.info_text.append(f"Середня різниця: {m:.2f}")
        if m < 1:
            self.ui.info_text.append("Візуальна різниця мінімальна")
        elif m < 10:
            self.ui.info_text.append("Незначна різниця")
        else:
            self.ui.info_text.append("Значна різниця")

    def reset_changes(self):
        if self.image is None:
            return
        self.modified_image = self.image.copy()
        self.original_lab_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2Lab)
        self.display_image(self.image, self.ui.modified_label)
        self.display_image(self.image, self.ui.compare_modified)
        self.ui.image_tabs.setCurrentIndex(0)
        self.ui.saturation_slider.setValue(0)
        self.ui.brightness_slider.setValue(0)
        self.ui.info_text.append("Зміни скинуто")
        self.update_button_states(True)

    def save_image(self):
        if self.modified_image is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти зображення", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;TIFF (*.tif *.tiff)"
        )
        if path:
            try:
                save_bgr = cv2.cvtColor(self.modified_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(path, save_bgr)
                self.ui.info_text.append(f"Збережено: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Помилка збереження: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ColorModelApp()
    win.setMinimumSize(1200, 800)
    win.show()
    sys.exit(app.exec())
