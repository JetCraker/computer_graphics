import sys
import math
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QGridLayout, QMessageBox, QSizePolicy, QFileDialog) # Додано QFileDialog
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QDoubleValidator, QFontMetrics, QMouseEvent, QWheelEvent
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF

import config
from geometry import (Trapezoid, get_translation_matrix,
                      get_scaling_matrix_around_point, get_rotation_matrix_around_point,
                      get_centroid, apply_transform)
from utils import save_matrix, save_vertices

class AnimationWidget(QWidget):
    """Widget for drawing the coordinate plane and animating the trapezoid."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(400, 300)

        self.trapezoid = None
        self.initial_vertices_np = None
        self.a, self.b, self.k, self.theta_radians = 0, 0, 1, 0
        self.zoom_level = config.INITIAL_ZOOM_LEVEL
        self.widget_center_x = 0
        self.widget_center_y = 0
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.last_pan_pos = None

        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(1000 // 60)
        self.animation_timer.timeout.connect(self._update_animation_step)

        self.current_time = 0.0
        self.is_forward_phase = True
        self.paused = True

        self.font = self.font()
        self.font_metrics = QFontMetrics(self.font)

    def set_trapezoid(self, vertices_np):
        """Sets the initial trapezoid."""
        try:
            self.trapezoid = Trapezoid(vertices_np)
            self.initial_vertices_np = vertices_np.copy()
            self.reset_animation_state() # Reset animation progress
            self.update() # Trigger repaint
        except ValueError as e:
            # Handle error (e.g., show message in main window)
            print(f"Error setting trapezoid: {e}")
            self.trapezoid = None
            self.initial_vertices_np = None

    def set_transform_params(self, a, b, k, theta_degrees):
        """Sets the transformation parameters."""
        self.a = a
        self.b = b
        self.k = k
        self.theta_radians = math.radians(theta_degrees)
        self.reset_animation_state()

    def start_pause_animation(self):
        """Toggles the animation timer."""
        if not self.trapezoid:
            return # Cannot animate without a trapezoid
        if self.paused:
            self.paused = False
            self.animation_timer.start()
        else:
            self.paused = True
            self.animation_timer.stop()
        return not self.paused # Return current running state

    def reset_animation_state(self):
        """Resets animation time and phase, keeping parameters."""
        self.current_time = 0.0
        self.is_forward_phase = True
        self.paused = True
        self.animation_timer.stop()
        if self.trapezoid:
            self.trapezoid.reset() # Reset to initial vertices
        self.update()

    def reset_view(self):
        """Resets zoom and pan."""
        self.zoom_level = config.INITIAL_ZOOM_LEVEL
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.widget_center_x = self.width() / 2
        self.widget_center_y = self.height() / 2
        self.update()

    def get_full_transform_matrix(self):
        """Calculates the full forward transformation matrix."""
        if not self.trapezoid or self.initial_vertices_np is None:
            return None
        try:
            centroid = get_centroid(self.initial_vertices_np)
            cx, cy = centroid
            trans_matrix = get_translation_matrix(self.a, self.b)
            scale_matrix = get_scaling_matrix_around_point(self.k, self.k, cx, cy)
            rot_matrix = get_rotation_matrix_around_point(self.theta_radians, cx, cy)
            # Order: Scale -> Rotate -> Translate
            full_forward_matrix = trans_matrix @ rot_matrix @ scale_matrix
            return full_forward_matrix
        except Exception as e:
            print(f"Error calculating full transform matrix: {e}")
            return None

    def _update_animation_step(self):
        """Calculates the transformation for the current animation frame."""
        try: # Add error handling
            if self.paused or not self.trapezoid or self.initial_vertices_np is None:
                return

            delta_time = self.animation_timer.interval() / 1000.0
            self.current_time += delta_time
            progress = min(self.current_time / config.ANIMATION_DURATION_SECONDS, 1.0)

            if self.is_forward_phase:
                current_a = self.a * progress
                current_b = self.b * progress
                current_k = 1.0 + (self.k - 1.0) * progress
                current_theta = self.theta_radians * progress
            else:
                current_a = self.a * (1.0 - progress)
                current_b = self.b * (1.0 - progress)
                current_k = 1.0 + (self.k - 1.0) * (1.0 - progress)
                current_theta = self.theta_radians * (1.0 - progress)

            self.trapezoid.reset() # Start from initial state
            initial_centroid = get_centroid(self.initial_vertices_np)
            cx, cy = initial_centroid

            step_translation = get_translation_matrix(current_a, current_b)
            step_scaling = get_scaling_matrix_around_point(current_k, current_k, cx, cy)
            step_rotation = get_rotation_matrix_around_point(current_theta, cx, cy)
            step_matrix = step_translation @ step_rotation @ step_scaling

            # Apply transform to initial vertices to get current state
            self.trapezoid.current_vertices = apply_transform(self.initial_vertices_np, step_matrix)

            if progress >= 1.0:
                self.current_time = 0.0
                self.is_forward_phase = not self.is_forward_phase
                print(f"Phase changed: {'Forward' if self.is_forward_phase else 'Backward'}")

            self.update() # Trigger repaint
        except Exception as e:
            print(f"Error during animation step: {e}")
            self.animation_timer.stop() # Stop timer on error
            self.paused = True
            # Optionally show an error message to the user via the main window

    def math_to_widget(self, x_math, y_math):
        """Converts mathematical coordinates to widget coordinates."""
        # Apply zoom and pan
        widget_x = self.widget_center_x + self.pan_offset_x + x_math * self.zoom_level
        widget_y = self.widget_center_y + self.pan_offset_y - y_math * self.zoom_level # Y is inverted
        return QPointF(widget_x, widget_y)

    def widget_to_math(self, x_widget, y_widget):
        """Converts widget coordinates to mathematical coordinates."""
        # Add check for zero zoom
        if abs(self.zoom_level) < 1e-9:
            return QPointF(0, 0) # Avoid division by zero
        math_x = (x_widget - self.widget_center_x - self.pan_offset_x) / self.zoom_level
        math_y = (self.widget_center_y + self.pan_offset_y - y_widget) / self.zoom_level # Y is inverted
        return QPointF(math_x, math_y)

    def paintEvent(self, event):
        """Draws the coordinate plane and the trapezoid."""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(self.rect(), Qt.white)

            width = self.width()
            height = self.height()

            # Prevent drawing if zoom is invalid
            if abs(self.zoom_level) < 1e-9:
                 painter.setPen(Qt.red)
                 painter.drawText(10, 20, "Error: Invalid zoom level")
                 return # Stop drawing

            # Calculate visible mathematical coordinate range
            math_top_left = self.widget_to_math(0, 0)
            math_bottom_right = self.widget_to_math(width, height)
            math_min_x = math_top_left.x()
            math_max_x = math_bottom_right.x()
            math_min_y = math_bottom_right.y() # Y is inverted in widget_to_math
            math_max_y = math_top_left.y()

            # --- Draw Grid and Axes ---
            grid_pen = QPen(QColor(*config.GRID_COLOR), 0.5, Qt.SolidLine)
            axis_pen = QPen(QColor(*config.AXIS_COLOR), 1.5, Qt.SolidLine)
            label_pen = QPen(QColor(*config.LABEL_COLOR), 1, Qt.SolidLine)
            painter.setFont(self.font)

            origin_widget = self.math_to_widget(0, 0)
            center_x = origin_widget.x()
            center_y = origin_widget.y()

            # Grid step calculation (simplified)
            step_pixels = config.GRID_STEP * self.zoom_level
            effective_grid_step = config.GRID_STEP
            min_pixel_step = 8 # Increase minimum pixel step slightly
            max_lines = 200 # Limit max number of grid lines to draw in each direction
            safety_counter = 0

            while step_pixels < min_pixel_step and safety_counter < 10:
                effective_grid_step *= 5
                step_pixels = effective_grid_step * self.zoom_level
                safety_counter += 1
            if step_pixels < min_pixel_step: step_pixels = min_pixel_step # Ensure minimum

            painter.setPen(grid_pen)
            # Vertical grid lines (draw only within visible math range)
            start_unit_x = math.floor(math_min_x / effective_grid_step) * effective_grid_step
            end_unit_x = math.ceil(math_max_x / effective_grid_step) * effective_grid_step
            line_count_x = 0
            unit_x = start_unit_x
            while unit_x <= end_unit_x and line_count_x < max_lines:
                widget_x = self.math_to_widget(unit_x, 0).x()
                painter.drawLine(int(widget_x), 0, int(widget_x), height)
                unit_x += effective_grid_step
                line_count_x += 1

            # Horizontal grid lines (draw only within visible math range)
            start_unit_y = math.floor(math_min_y / effective_grid_step) * effective_grid_step
            end_unit_y = math.ceil(math_max_y / effective_grid_step) * effective_grid_step
            line_count_y = 0
            unit_y = start_unit_y
            while unit_y <= end_unit_y and line_count_y < max_lines:
                widget_y = self.math_to_widget(0, unit_y).y()
                painter.drawLine(0, int(widget_y), width, int(widget_y))
                unit_y += effective_grid_step
                line_count_y += 1

            # Axes
            painter.setPen(axis_pen)
            painter.drawLine(0, int(center_y), width, int(center_y)) # X-axis
            painter.drawLine(int(center_x), 0, int(center_x), height) # Y-axis

            # Axis Labels and Ticks (draw only within visible range)
            painter.setPen(label_pen)
            tick_len = 5
            label_margin = 2
            # X-axis ticks and labels
            unit_x = start_unit_x # Reuse calculated start/end
            line_count_x = 0
            while unit_x <= end_unit_x and line_count_x < max_lines:
                 widget_x = self.math_to_widget(unit_x, 0).x()
                 # Check proximity to origin widget coordinates more robustly
                 if abs(widget_x - center_x) > tick_len * 1.5: # Don't draw label too close to Y axis
                     painter.drawLine(int(widget_x), int(center_y - tick_len), int(widget_x), int(center_y + tick_len))
                     label = str(int(unit_x) if abs(unit_x - int(unit_x)) < 1e-6 else round(unit_x, 2))
                     text_width = self.font_metrics.horizontalAdvance(label)
                     # Ensure label is within widget bounds horizontally
                     label_x_pos = max(0, min(width - text_width, int(widget_x - text_width / 2)))
                     painter.drawText(label_x_pos, int(center_y + tick_len + self.font_metrics.ascent() + label_margin), label)
                 unit_x += effective_grid_step
                 line_count_x += 1

            # Y-axis ticks and labels
            unit_y = start_unit_y # Reuse calculated start/end
            line_count_y = 0
            while unit_y <= end_unit_y and line_count_y < max_lines:
                 widget_y = self.math_to_widget(0, unit_y).y()
                 if abs(widget_y - center_y) > tick_len * 1.5: # Don't draw label too close to X axis
                     painter.drawLine(int(center_x - tick_len), int(widget_y), int(center_x + tick_len), int(widget_y))
                     label = str(int(unit_y) if abs(unit_y - int(unit_y)) < 1e-6 else round(unit_y, 2))
                     text_height = self.font_metrics.height()
                     text_width = self.font_metrics.horizontalAdvance(label)
                     # Ensure label is within widget bounds vertically
                     label_y_pos = max(text_height, min(height, int(widget_y + text_height / 4)))
                     painter.drawText(max(0, int(center_x - tick_len - text_width - label_margin)), label_y_pos, label)
                 unit_y += effective_grid_step
                 line_count_y += 1

            # Origin Label "0"
            painter.drawText(int(center_x + label_margin + tick_len), int(center_y + self.font_metrics.ascent() + label_margin + tick_len), "0")
            # Axis Names "X", "Y"
            painter.drawText(width - self.font_metrics.horizontalAdvance("X") - 5, int(center_y - 5), "X")
            painter.drawText(int(center_x + 5), self.font_metrics.ascent() + 5, "Y")


            # --- Draw Trapezoid ---
            if self.trapezoid and self.trapezoid.current_vertices is not None:
                polygon = QPolygonF()
                valid_polygon = True
                for x_math, y_math in self.trapezoid.current_vertices:
                    # Check for NaN or Inf values before transforming
                    if not (math.isfinite(x_math) and math.isfinite(y_math)):
                        valid_polygon = False
                        print(f"Warning: Invalid vertex coordinate detected ({x_math}, {y_math})")
                        break
                    polygon.append(self.math_to_widget(x_math, y_math))

                if valid_polygon and len(polygon) == 4:
                    color = config.TRAPEZOID_COLOR_FORWARD if self.is_forward_phase else config.TRAPEZOID_COLOR_BACKWARD
                    painter.setBrush(QBrush(QColor(*color)))
                    painter.setPen(QPen(QColor(*config.BLACK), 1)) # Border pen
                    painter.drawPolygon(polygon)
                elif not valid_polygon:
                     painter.setPen(Qt.red)
                     painter.drawText(10, 40, "Error: Invalid trapezoid coordinates")


        except Exception as e:
            print(f"Error during paintEvent: {e}")
            painter.setPen(Qt.red)
            painter.drawText(10, 20, f"Drawing Error: {e}")
        finally:
            # Ensure painter is ended even if errors occurred before painter.end()
            if painter.isActive():
                painter.end()

    def resizeEvent(self, event):
        """Update center when widget is resized."""
        # Calculate center based on new size
        self.widget_center_x = event.size().width() / 2
        self.widget_center_y = event.size().height() / 2
        # No need to call super().resizeEvent(event) for basic QWidget
        self.update() # Trigger repaint with new size

    def wheelEvent(self, event: QWheelEvent):
        # Add check for zero zoom before applying factor
        if abs(self.zoom_level) < 1e-9: return

        steps = event.angleDelta().y() / 120
        # Use multiplicative zoom step from config
        factor = config.ZOOM_STEP ** steps # factor = 1.1^steps or 1.1^-steps

        old_zoom = self.zoom_level
        new_zoom = old_zoom * factor
        # Clamp zoom level
        self.zoom_level = max(config.MIN_ZOOM, min(config.MAX_ZOOM, new_zoom))

        # Prevent division by zero if old_zoom was somehow invalid
        if abs(old_zoom) < 1e-9:
            zoom_ratio = 1.0
        else:
            zoom_ratio = self.zoom_level / old_zoom

        # Zoom towards the mouse cursor
        mouse_pos = event.position()
        self.pan_offset_x = mouse_pos.x() - (mouse_pos.x() - self.pan_offset_x) * zoom_ratio
        self.pan_offset_y = mouse_pos.y() - (mouse_pos.y() - self.pan_offset_y) * zoom_ratio

        print(f"Zoom: {self.zoom_level:.1f}")
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Start panning when the mouse button is pressed."""
        if event.button() == Qt.LeftButton:
            self.last_pan_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Update pan offset during mouse drag."""
        if self.last_pan_pos is not None:
            delta = event.position() - self.last_pan_pos
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_pan_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop panning when the mouse button is released."""
        if event.button() == Qt.LeftButton and self.last_pan_pos is not None:
            self.last_pan_pos = None
            self.setCursor(Qt.ArrowCursor)


class MainWindow(QMainWindow):
    """Main application window with controls and animation widget."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trapezoid Animation (PySide6)")
        self.setGeometry(100, 100, 900, 700) # Initial window size and position

        self.animation_widget = AnimationWidget()
        self.validator = QDoubleValidator(-1000.0, 1000.0, 2) # Validator for inputs
        self.scale_validator = QDoubleValidator(0.01, 1000.0, 2) # Scale must be positive

        # --- Input Widgets ---
        self.vertex_inputs = []
        input_layout = QGridLayout()
        input_layout.addWidget(QLabel("Вершини трапеції (x y):"), 0, 0, 1, 4)
        for i in range(4):
            label = QLabel(f"Вершина {i+1}:")
            x_edit = QLineEdit()
            y_edit = QLineEdit()
            x_edit.setValidator(self.validator)
            y_edit.setValidator(self.validator)
            x_edit.setPlaceholderText("x")
            y_edit.setPlaceholderText("y")
            input_layout.addWidget(label, i + 1, 0)
            input_layout.addWidget(x_edit, i + 1, 1)
            input_layout.addWidget(y_edit, i + 1, 2)
            self.vertex_inputs.append((x_edit, y_edit))

        # Додаємо кнопку завантаження вершин
        self.load_vertices_button = QPushButton("Завантажити вершини")
        self.load_vertices_button.clicked.connect(self._load_vertices_from_file)
        input_layout.addWidget(self.load_vertices_button, 5, 0, 1, 3) # Розміщуємо її перед параметрами

        input_layout.addWidget(QLabel("Параметри трансформації:"), 6, 0, 1, 4) # Зміщуємо індекси рядків
        self.a_edit = QLineEdit("0")
        self.b_edit = QLineEdit("0")
        self.k_edit = QLineEdit("1.5")
        self.theta_edit = QLineEdit("45")
        self.a_edit.setValidator(self.validator)
        self.b_edit.setValidator(self.validator)
        self.k_edit.setValidator(self.scale_validator)
        self.theta_edit.setValidator(self.validator) # Allow negative angles

        input_layout.addWidget(QLabel("Переміщення a:"), 7, 0) # Зміщуємо індекси рядків
        input_layout.addWidget(self.a_edit, 7, 1)
        input_layout.addWidget(QLabel("Переміщення b:"), 8, 0) # Зміщуємо індекси рядків
        input_layout.addWidget(self.b_edit, 8, 1)
        input_layout.addWidget(QLabel("Масштаб k (>0):"), 9, 0) # Зміщуємо індекси рядків
        input_layout.addWidget(self.k_edit, 9, 1)
        input_layout.addWidget(QLabel("Кут theta (°):"), 10, 0) # Зміщуємо індекси рядків
        input_layout.addWidget(self.theta_edit, 10, 1)

        self.submit_button = QPushButton("Застосувати введення")
        self.submit_button.clicked.connect(self._apply_inputs)
        input_layout.addWidget(self.submit_button, 11, 0, 1, 3) # Зміщуємо індекси рядків

        # --- Control Buttons ---
        self.start_pause_button = QPushButton("Start")
        self.save_matrix_button = QPushButton("Зберегти матрицю")
        self.reset_view_button = QPushButton("Скинути вигляд")

        self.start_pause_button.clicked.connect(self._toggle_animation)
        self.save_matrix_button.clicked.connect(self._save_matrix)
        self.reset_view_button.clicked.connect(self.animation_widget.reset_view)

        # Disable controls initially
        self.start_pause_button.setEnabled(False)
        self.save_matrix_button.setEnabled(False)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_pause_button)
        controls_layout.addWidget(self.save_matrix_button)
        controls_layout.addWidget(self.reset_view_button)
        controls_layout.addStretch()

        # --- Main Layout ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addLayout(input_layout)
        left_layout.addStretch() # Push inputs to the top
        left_panel.setMaximumWidth(250) # Limit width of input panel

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.animation_widget) # Animation widget takes remaining space

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Combine central widget and bottom controls
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(central_widget)
        outer_layout.addLayout(controls_layout)

        container_widget = QWidget()
        container_widget.setLayout(outer_layout)
        self.setCentralWidget(container_widget)

    def _load_vertices_from_file(self):
        """Opens a file dialog to load initial trapezoid vertices."""
        # Використовуємо поточну директорію або директорію конфігураційного файлу як початкову
        start_dir = "." # Або можна вказати конкретний шлях
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Завантажити початкові вершини",
            start_dir,
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            try:
                # Завантажуємо дані, пропускаючи можливий рядок заголовка
                loaded_vertices = np.loadtxt(filename, comments='#')

                if loaded_vertices.shape != (4, 2):
                    raise ValueError(f"Файл '{filename}' повинен містити 4 рядки та 2 стовпці координат. Знайдено форму: {loaded_vertices.shape}")

                # Заповнюємо поля введення
                for i, (x_edit, y_edit) in enumerate(self.vertex_inputs):
                    x_edit.setText(str(loaded_vertices[i, 0]))
                    y_edit.setText(str(loaded_vertices[i, 1]))

                QMessageBox.information(self, "Успіх", f"Вершини завантажено з '{filename}'.\nТепер натисніть 'Застосувати введення'.")
                # Не викликаємо _apply_inputs автоматично, щоб користувач міг перевірити/змінити параметри трансформації

            except FileNotFoundError:
                QMessageBox.warning(self, "Помилка", f"Файл не знайдено: {filename}")
            except ValueError as e:
                QMessageBox.warning(self, "Помилка формату файлу", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Помилка читання файлу", f"Не вдалося прочитати файл '{filename}': {e}")


    def _apply_inputs(self):
        """Reads and validates inputs (from fields), then updates the animation widget."""
        vertices = []
        try:
            # --- Зчитування вершин з полів вводу ---
            for i, (x_edit, y_edit) in enumerate(self.vertex_inputs):
                x_str = x_edit.text().strip().replace(',', '.')
                y_str = y_edit.text().strip().replace(',', '.')
                if not x_str or not y_str:
                    # Дозволяємо порожні поля, якщо вони були заповнені з файлу,
                    # але якщо користувач їх очистив, то це помилка.
                    # Краще завжди вимагати заповнені поля перед застосуванням.
                    raise ValueError(f"Вершина {i+1}: Координати не можуть бути порожніми.")
                x = float(x_str)
                y = float(y_str)
                vertices.append([x, y])

            if len(vertices) != 4:
                 raise ValueError("Потрібно ввести 4 вершини.") # Should not happen with UI structure

            vertices_np = np.array(vertices, dtype=float)
            # Зберігаємо початкові вершини ТІЛЬКИ якщо вони були введені вручну або змінені
            # Якщо вони щойно завантажені, не перезаписуємо файл одразу
            # Можна додати прапорець, чи були дані змінені після завантаження
            # Або просто зберігати при кожному застосуванні
            try:
                save_vertices(vertices_np, config.INITIAL_VERTICES_FILENAME)
                print(f"Поточні початкові координати збережено у '{config.INITIAL_VERTICES_FILENAME}'")
            except Exception as save_err:
                 print(f"Попередження: Не вдалося зберегти початкові координати: {save_err}")


            self.animation_widget.set_trapezoid(vertices_np)

            # --- Зчитування параметрів трансформації ---
            a_str = self.a_edit.text().strip().replace(',', '.')
            b_str = self.b_edit.text().strip().replace(',', '.')
            k_str = self.k_edit.text().strip().replace(',', '.')
            theta_str = self.theta_edit.text().strip().replace(',', '.')

            if not all([a_str, b_str, k_str, theta_str]):
                 raise ValueError("Параметри трансформації не можуть бути порожніми.")

            a = float(a_str)
            b = float(b_str)
            k = float(k_str)
            theta = float(theta_str)

            if k <= 0:
                raise ValueError("Коефіцієнт масштабування k має бути > 0.")

            self.animation_widget.set_transform_params(a, b, k, theta)

            # Enable controls now that we have valid input
            self.start_pause_button.setEnabled(True)
            self.save_matrix_button.setEnabled(True)
            self.start_pause_button.setText("Start") # Reset button text

            QMessageBox.information(self, "Успіх", "Дані застосовано. Можна починати анімацію.")

        except ValueError as e:
            QMessageBox.warning(self, "Помилка введення", str(e))
            # Не вимикаємо кнопки, якщо помилка лише в параметрах трансформації,
            # а вершини вже були успішно задані/завантажені.
            # self.start_pause_button.setEnabled(False)
            # self.save_matrix_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Критична помилка", f"Не вдалося обробити введення: {e}")
            self.start_pause_button.setEnabled(False)
            self.save_matrix_button.setEnabled(False)

    def _toggle_animation(self):
        """Starts or pauses the animation."""
        is_running = self.animation_widget.start_pause_animation()
        self.start_pause_button.setText("Pause" if is_running else "Start")

    def _save_matrix(self):
        """Saves the full forward transformation matrix."""
        matrix = self.animation_widget.get_full_transform_matrix()
        if matrix is not None:
            try:
                save_matrix(matrix, config.TRANSFORMATION_MATRIX_FILENAME)
                QMessageBox.information(self, "Збереження", f"Матрицю перетворення збережено у\n'{config.TRANSFORMATION_MATRIX_FILENAME}'")
            except Exception as e:
                 QMessageBox.critical(self, "Помилка збереження", f"Не вдалося зберегти матрицю: {e}")
        else:
             QMessageBox.warning(self, "Помилка", "Не вдалося обчислити матрицю. Перевірте введені дані.")

