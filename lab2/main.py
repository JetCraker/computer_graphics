import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog, QTextEdit, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from graph import Ui_MainWindow

curves = []
active_curve_index = -1


def bernstein(n, i, t):
    return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))


def bezier_curve(x, y, t):
    if len(x) == 1:
        return x[0], y[0]

    new_points_x = []
    new_points_y = []

    for i in range(len(x) - 1):
        new_x = (1 - t) * x[i] + t * x[i + 1]
        new_y = (1 - t) * y[i] + t * y[i + 1]
        new_points_x.append(new_x)
        new_points_y.append(new_y)

    return bezier_curve(new_points_x, new_points_y, t)


class TriangleAPP(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)  # додаємо єдину область для побудови графіка
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self.ui.widget)  # створюємо вертикальний макет
        layout.setContentsMargins(0, 0, 0, 0)  # мінімальні відступи
        layout.addWidget(self.canvas)  # додаємо полотно для відображення графіка
        layout.addWidget(self.toolbar)  # додаємо панель інструментів для графіка

        self.ui.CreateButton.clicked.connect(self.create_reference_points)
        self.ui.ClearButton.clicked.connect(self.clear)
        self.ui.Bezier_curve_but.clicked.connect(self.bezier_curve_draw)
        self.ui.bernstein_button.clicked.connect(self.compute_bernstein)
        self.ui.NewCurveButton.clicked.connect(self.create_new_curve)
        self.ui.Parametric_curve_but.clicked.connect(self.parametric_curve_draw)

        self.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)

        # Видаляємо QTimer – тепер оновлення відбувається лише при натисканні кнопок або при переміщенні точок

        self.ax.axhline(0, color="black", linewidth=1)
        self.ax.axvline(0, color="black", linewidth=1)
        self.ax.grid(True)

    def create_new_curve(self):
        """Створює нову активну криву"""
        global active_curve_index
        curves.append(([], []))
        active_curve_index = len(curves) - 1  # робимо її активною
        self.ui.error_label.setText(f"Створено нову криву №{active_curve_index + 1}")

    def create_reference_points(self):
        """Створює точки для кривої"""
        global active_curve_index
        if active_curve_index == -1:
            self.ui.error_label.setText("Спершу створіть нову криву!")
            return

        try:
            x1 = int(self.ui.X1_lineEdit.text())
            y1 = int(self.ui.Y1_lineEdit.text())

            # Додаємо точку до активної кривої
            curves[active_curve_index][0].append(x1)
            curves[active_curve_index][1].append(y1)

            # Якщо словник для збереження ліній не створено, створюємо його
            if not hasattr(self, 'curve_lines'):
                self.curve_lines = {}

            self.update_curve_plot(active_curve_index)

            # Оновлюємо межі графіка за всіма точками усіх кривих
            all_x = [x for crv in curves for x in crv[0]]
            all_y = [y for crv in curves for y in crv[1]]
            if all_x and all_y:
                self.ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
                self.ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

            self.ax.grid(True)
            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def bezier_curve_draw(self):
        """Малює криву Безьє для активної множини точок."""
        global active_curve_index
        if active_curve_index == -1 or len(curves[active_curve_index][0]) < 2:
            self.ui.error_label.setText("Додайте хоча б дві точки!")
            return

        try:
            color = self.ui.Color_lineEdit.text()
            step = float(self.ui.step_lineEdit.text())

            if step <= 0 or step > 1:
                self.ui.error_label.setText("Крок має бути у межах (0, 1]!")
                return

            curve_x, curve_y = [], []
            t = 0.0
            while t <= 1:
                bx, by = bezier_curve(curves[active_curve_index][0], curves[active_curve_index][1], t)
                curve_x.append(bx)
                curve_y.append(by)
                t += step

            if not hasattr(self, 'bezier_lines'):
                self.bezier_lines = {}

            if active_curve_index in self.bezier_lines:
                try:
                    self.bezier_lines[active_curve_index].remove()
                except ValueError:
                    pass

            bezier_line, = self.ax.plot(curve_x, curve_y, color=color,
                                        label=f"Крива Безьє №{active_curve_index + 1}")
            self.bezier_lines[active_curve_index] = bezier_line

            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def parametric_curve_draw(self):
        """Малює криву Безьє параметричним способом"""
        global active_curve_index
        if active_curve_index == -1 or len(curves[active_curve_index][0]) < 2:
            self.ui.error_label.setText("Додайте хоча б дві точки!")
            return

        try:
            color = self.ui.Color_lineEdit.text()
            step = float(self.ui.step_lineEdit.text())

            if step <= 0 or step > 1:
                self.ui.error_label.setText("Крок має бути у межах (0, 1]!")
                return

            n = len(curves[active_curve_index][0]) - 1
            t_values = [i * step for i in range(int(1 / step) + 1)]

            curve_x = []
            curve_y = []

            for t in t_values:
                x_t = sum(bernstein(n, i, t) * curves[active_curve_index][0][i] for i in range(n + 1))
                y_t = sum(bernstein(n, i, t) * curves[active_curve_index][1][i] for i in range(n + 1))
                curve_x.append(x_t)
                curve_y.append(y_t)

            if not hasattr(self, 'parametric_lines'):
                self.parametric_lines = {}

            if active_curve_index in self.parametric_lines:
                try:
                    self.parametric_lines[active_curve_index].remove()
                except ValueError:
                    pass

            parametric_line, = self.ax.plot(curve_x, curve_y, color=color,
                                            label=f"Парам. Безьє №{active_curve_index + 1}")
            self.parametric_lines[active_curve_index] = parametric_line

            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def compute_bernstein(self):
        # Перевіряємо, що є хоча б 3 контрольні точки (щоб були внутрішні точки)
        if not curves or len(curves[-1][0]) < 3:
            self.ui.error_label.setText(
                "Потрібно мати принаймні 3 контрольні точки для обчислення внутрішніх поліномів!")
            return

        try:
            step = float(self.ui.step_lineEdit.text())
            if step <= 0 or step > 1:
                self.ui.error_label.setText("Крок має бути у межах (0, 1]!")
                return

            n_points = len(curves[-1][0])
            degree = n_points - 1

            t_values = [round(i * step, 2) for i in range(int(1 / step) + 1)]

            bernstein_table = {
                t: [bernstein(degree, i, t) for i in range(1, n_points - 1)]
                for t in t_values
            }

            result_text = f"Внутрішні Bernstein поліноми для кривої №{len(curves)}:\n"
            for t, values in bernstein_table.items():
                result_text += f"t = {t}: {values}\n"

            self.show_modal_window("Внутрішні Bernstein поліноми", result_text)
            self.ui.error_label.setText("")
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def update_curve_plot(self, index):
        # Отримуємо координати контрольних точок
        x_points = curves[index][0]
        y_points = curves[index][1]

        # Оновлюємо лінію, що з'єднує контрольні точки
        if hasattr(self, 'curve_lines') and index in self.curve_lines:
            self.curve_lines[index].set_data(x_points, y_points)
        else:
            line, = self.ax.plot(x_points, y_points, '-', color='black', label=f"Крива №{index + 1}")
            if not hasattr(self, 'curve_lines'):
                self.curve_lines = {}
            self.curve_lines[index] = line

        if len(x_points) == 0:
            return
        elif len(x_points) == 1:
            colors = ['red']
        elif len(x_points) == 2:
            colors = ['red', 'red']
        else:
            colors = ['red'] + ['black'] * (len(x_points) - 2) + ['red']

        points = list(zip(x_points, y_points))
        if hasattr(self, 'control_points_scatter') and index in self.control_points_scatter:
            scatter = self.control_points_scatter[index]
            scatter.set_offsets(points)
            scatter.set_facecolors(colors)
        else:
            scatter = self.ax.scatter(x_points, y_points, c=colors)
            if not hasattr(self, 'control_points_scatter'):
                self.control_points_scatter = {}
            self.control_points_scatter[index] = scatter

        self.canvas.draw_idle()

    def clear(self):
        global active_curve_index, curves
        if active_curve_index == -1:
            self.ui.error_label.setText("Спочатку створіть криву!")
            return

        if hasattr(self, 'curve_lines'):
            for line in self.curve_lines.values():
                line.remove()
            self.curve_lines.clear()

        if hasattr(self, 'bezier_lines'):
            for bezier in self.bezier_lines.values():
                bezier.remove()
            self.bezier_lines.clear()

        if hasattr(self, 'parametric_lines'):
            for parametric in self.parametric_lines.values():
                parametric.remove()
            self.parametric_lines.clear()

        if hasattr(self, 'control_points_scatter'):
            for scatter in self.control_points_scatter.values():
                scatter.remove()
            self.control_points_scatter.clear()

        curves.clear()

        if self.ax.get_legend():
            self.ax.get_legend().remove()

        self.canvas.draw()

    def on_scroll(self, event):
        scale_factor = 1.2 if event.step > 0 else 0.8
        self.ax.set_xlim([x * scale_factor for x in self.ax.get_xlim()])
        self.ax.set_ylim([y * scale_factor for y in self.ax.get_ylim()])
        self.canvas.draw()

    def show_modal_window(self, title, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(800, 800)

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setText(text)
        text_edit.setReadOnly(True)

        close_button = QPushButton("Закрити")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(text_edit)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def on_button_press(self, event):
        global active_curve_index
        if active_curve_index == -1 or event.inaxes is None:
            return

        if event.button == 1 and event.dblclick:
            curves[active_curve_index][0].append(event.xdata)
            curves[active_curve_index][1].append(event.ydata)
            self.update_curve_plot(active_curve_index)
        elif event.button == 3:
            threshold = 1.0  # поріг вибору
            closest_point = None
            min_dist = float('inf')
            for i, (x, y) in enumerate(zip(curves[active_curve_index][0], curves[active_curve_index][1])):
                dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_point = i
            if min_dist < threshold:
                self.dragging_point = closest_point
                print(f"Вибрана точка для перетягування: {closest_point}")
            else:
                self.dragging_point = None

    def on_motion(self, event):
        global active_curve_index
        if not hasattr(self, 'dragging_point') or self.dragging_point is None or event.inaxes is None:
            return

        curves[active_curve_index][0][self.dragging_point] = event.xdata
        curves[active_curve_index][1][self.dragging_point] = event.ydata

        self.update_curve_plot(active_curve_index)

        # Якщо крива вже була побудована, оновлюємо її динамічно:
        if hasattr(self, 'bezier_lines') and active_curve_index in self.bezier_lines:
            self.bezier_curve_draw()
        if hasattr(self, 'parametric_lines') and active_curve_index in self.parametric_lines:
            self.parametric_curve_draw()

    def on_release(self, event):
        self.dragging_point = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TriangleAPP()
    window.show()
    sys.exit(app.exec())
