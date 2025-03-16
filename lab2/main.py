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

    new_points_x = list()
    new_points_y = list()

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
        self.ax = self.fig.add_subplot(111) #  додає єдину область для побудови графіка.
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self.ui.widget) # створює вертикальний макет
        layout.setContentsMargins(0, 0, 0, 0)  # мінімальні відступи
        layout.addWidget(self.canvas) # додає полотно для відображення графіка.
        layout.addWidget(self.toolbar) # додає панель інструментів для графіка.

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

        self.ax.axhline(0, color="black", linewidth=1)
        self.ax.axvline(0, color="black", linewidth=1)
        self.ax.grid(True)

    def create_new_curve(self):
        global active_curve_index
        curves.append(([], []))
        active_curve_index = len(curves) - 1  # Робимо її активною
        self.ui.error_label.setText(f"Створено нову криву №{active_curve_index + 1}")

    def create_reference_points(self):
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

            # Якщо лінія для активної кривої вже існує, оновлюємо її дані,
            # інакше створюємо нову лінію для активної кривої
            if active_curve_index in self.curve_lines:
                line = self.curve_lines[active_curve_index]
                line.set_data(curves[active_curve_index][0], curves[active_curve_index][1])
            else:
                line, = self.ax.plot(curves[active_curve_index][0],
                                     curves[active_curve_index][1],
                                     'o-',
                                     color='black',
                                     label=f"Крива №{active_curve_index + 1}")
                self.curve_lines[active_curve_index] = line

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
                self.bezier_lines = []

            bezier_line, = self.ax.plot(curve_x, curve_y, color=color, label=f"Крива Безьє №{active_curve_index + 1}")
            self.bezier_lines.append(bezier_line)

            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def parametric_curve_draw(self):
        global active_curve_index
        if active_curve_index == -1 or len(curves[active_curve_index][0]) < 2:
            self.ui.error_label.setText("Додайте хоча б дві точки!")
            return

        try:
            color = self.ui.Color_lineEdit.text()
            step = float(self.ui.step_lineEdit.text())

            if step <= 0 or step > 1:
                self.ui.error_label.setText("Крок має бути у межах (0, 1]")
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
                self.parametric_lines = []

            parametric_line, = self.ax.plot(curve_x, curve_y, color=color,
                                            label=f"Парам. Безьє №{active_curve_index + 1}")
            self.parametric_lines.append(parametric_line)

            self.ax.legend()
            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def compute_bernstein(self):
        if not curves or len(curves[-1][0]) < 2:
            self.ui.error_label.setText("Має бути хоча б 2 контрольні точки!")
            return

        try:
            step = float(self.ui.step_lineEdit.text())
            if step <= 0 or step > 1:
                self.ui.error_label.setText("Крок має бути у межах (0, 1]!")
                return

            n = len(curves[-1][0]) - 1
            t_values = [round(i * step, 2) for i in range(int(1 / step) + 1)]
            bernstein_table = {t: [bernstein(n, i, t) for i in range(n + 1)] for t in t_values}

            result_text = f"Поліноми Бернштейна для кривої №{len(curves)}:\n"
            for t, values in bernstein_table.items():
                result_text += f"t = {t}: {values}\n"

            self.show_modal_window("Поліноми Бернштейна", result_text)
            self.ui.error_label.setText("")

        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

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
            for bezier in self.bezier_lines:
                bezier.remove()
            self.bezier_lines.clear()

        if hasattr(self, 'parametric_lines'):
            for parametric in self.parametric_lines:
                parametric.remove()
            self.parametric_lines.clear()

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
        """Функція для створення модального вікна"""
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
        """
        Об'єднаний обробник події натискання миші:
        - Ліва кнопка (1) + подвійний клік – додаємо нову точку.
        - Права кнопка (3) – запускаємо режим перетягування, вибираючи точку з мінімальною відстанню.
        """
        global active_curve_index
        if active_curve_index == -1 or event.inaxes is None:
            return

        # Якщо подвійний лівий клік – додаємо точку
        if event.button == 1 and event.dblclick:
            curves[active_curve_index][0].append(event.xdata)
            curves[active_curve_index][1].append(event.ydata)
            if not hasattr(self, 'curve_lines'):
                self.curve_lines = {}
            if active_curve_index in self.curve_lines:
                line = self.curve_lines[active_curve_index]
                line.set_data(curves[active_curve_index][0], curves[active_curve_index][1])
            else:
                line, = self.ax.plot(curves[active_curve_index][0],
                                     curves[active_curve_index][1],
                                     'o-',
                                     color='black',
                                     label=f"Крива №{active_curve_index + 1}")
                self.curve_lines[active_curve_index] = line
            self.ax.legend()
            self.canvas.draw()

        # Якщо права кнопка – шукаємо найближчу точку для перетягування
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
        """Переміщення вибраної контрольної точки під час руху миші."""
        if (not hasattr(self, 'dragging_point') or self.dragging_point is None or
                event.inaxes is None):
            return

        # Оновлюємо координати вибраної точки
        curves[active_curve_index][0][self.dragging_point] = event.xdata
        curves[active_curve_index][1][self.dragging_point] = event.ydata

        # Оновлюємо графічну лінію
        if active_curve_index in self.curve_lines:
            line = self.curve_lines[active_curve_index]
            line.set_data(curves[active_curve_index][0], curves[active_curve_index][1])
        self.canvas.draw()

    def on_release(self, event):
        self.dragging_point = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TriangleAPP()
    window.show()
    sys.exit(app.exec())
