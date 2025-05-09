import sys
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QColorDialog

from graph import Ui_MainWindow


class FractalCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(FractalCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()


class HyperbolicSinusFractal:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.max_iterations = 100
        self.escape_radius = 1000
        self.x_min, self.x_max = -2.5, 2.5
        self.y_min, self.y_max = -2.0, 2.0
        self.colormap = 'viridis'

    def generate(self, c_real, c_imag):
        # Створення масивів для осей x та y
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        # Об'єднуємо дійсні та уявні частини в одне комплексне число c
        c = complex(c_real, c_imag)

        # Ініціалізація матриці результатів - кожен піксель спочатку має значення 0
        result = np.zeros((self.height, self.width))

        # Створення комплексної сітки точок
        # np.meshgrid створює дві матриці: X з значеннями x та Y з значеннями y
        X, Y = np.meshgrid(x, y)
        # Кожну точку перетворюємо у комплексне число: z = x + iy
        Z = X + 1j * Y

        # Робимо копію початкової сітки, над якою будемо робити обчислення
        Z_temp = np.copy(Z)

        # Основний цикл ітерацій (до max_iterations разів)
        for i in range(self.max_iterations):
            # Якщо величина (абсолютне значення) будь-якого з чисел більша за 700,
            # ми вважаємо, що точка «втікла» (тобто, стала занадто великою)
            mask_overflow = np.abs(Z_temp) > 700
            if np.any(mask_overflow):
                # Для тих точок, які ще не були зафіксовані (result==0),
                # записуємо номер ітерації i
                result[mask_overflow & (result == 0)] = i
                # Призначаємо значення нескінченності, щоб більше з цією точкою не працювати
                Z_temp[mask_overflow] = np.inf

            # Застосування функції: обчислюємо sinh(z) та додаємо комплексну константу c
            # Наприклад, якщо Z_temp = 1 + 1i, тоді: sinh(1+1i) + c обчислюється для кожного елемента
            try:
                Z_temp = np.sinh(Z_temp) + c
            except:
                # Якщо виникають проблеми з числовими помилками, встановлюємо їх як Inf
                Z_temp[np.isnan(Z_temp) | np.isinf(Z_temp)] = np.inf

            # Перевірка "втечі": якщо значення стало занадто великим, знову записуємо номер ітерації
            mask = (np.abs(Z_temp) > self.escape_radius) & (result == 0)
            result[mask] = i

            # Якщо майже всі точки (менше 1% залишилось оброблятись) вже "втікли", припиняємо цикл
            if np.sum(result == 0) < (self.width * self.height * 0.01):
                break

        # Нормалізація: ділимо кожне число з result на максимальну кількість ітерацій,
        # щоб всі значення знаходилися в діапазоні від 0 до 1
        normalized = result / self.max_iterations
        return normalized


class HilbertCurve:
    def __init__(self):
        self.iterations = 5
        self.size = 800
        self.line_width = 1
        self.color = "blue"

    def _get_hilbert_points(self, iterations):
        def rot(n, x, y, rx, ry):
            # Якщо ry == 0, це означає, що ми повинні повернути точку для отримання правильної орієнтації
            if ry == 0:
                if rx == 1:
                    # Якщо rx == 1, відображаємо (інвертуємо) координати в межах квадрату розміру n
                    x = n - 1 - x
                    y = n - 1 - y
                # Міняємо місцями x та y
                x, y = y, x
            return x, y

        def d2xy(n, d):
            x = y = 0
            # s представляє поточну «роздільну здатність» у квадраті
            s = 1
            while s < n:
                # rx отримуємо за допомогою бітової операції: перевіряємо певний біт числа d
                rx = 1 & (d // 2)
                # ry визначається за допомогою виключного АБО (XOR) з rx
                ry = 1 & (d ^ rx)
                # Використовуємо функцію повороту, щоб скоригувати x та y
                x, y = rot(s, x, y, rx, ry)
                # Коригуємо координати: додаємо s*rx до x та s*ry до y
                x += s * rx
                y += s * ry
                # Зменшуємо d, «видаляючи» оброблену частину (поділ на 4)
                d //= 4
                # Збільшуємо s у 2 рази для наступного рівня детальності
                s *= 2
            return x, y

        # n визначає розмір сітки по одному краю. Наприклад, при iterations = 3: n = 2^3 = 8.
        n = 2 ** iterations
        # Загальна кількість точок у сітці: квадрат із n x n точок.
        total_points = n * n

        points = []
        # Для кожного порядкового номера від 0 до total_points - 1
        for i in range(total_points):
            # Обчислюємо координати (x, y) для даної позиції уздовж кривої
            x, y = d2xy(n, i)
            # Нормалізуємо координати, ділячи їх на (n - 1)
            # Так ми отримуємо значення в діапазоні [0, 1], що зручно для побудови графіку
            points.append([x / (n - 1), y / (n - 1)])
        return points


class FractalVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sinh_fractal = HyperbolicSinusFractal()
        self.hilbert_curve = HilbertCurve()

        self.current_xlim = None
        self.current_ylim = None

        self.fractal_generated = False

        self.setup_canvases()

        self.connect_signals()

    def setup_canvases(self):
        self.sinh_canvas = FractalCanvas(width=8, height=7, dpi=100)
        self.sinh_nav_toolbar = NavigationToolbar2QT(self.sinh_canvas, self)
        self.ui.sinh_left_layout.addWidget(self.sinh_canvas)
        self.ui.sinh_left_layout.addWidget(self.sinh_nav_toolbar)

        self.sinh_canvas.mpl_connect('draw_event', self.on_sinh_draw)
        self.sinh_canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        self.hilbert_canvas = FractalCanvas(width=8, height=7, dpi=100)
        self.hilbert_nav_toolbar = NavigationToolbar2QT(self.hilbert_canvas, self)
        self.ui.hilbert_left_layout.addWidget(self.hilbert_canvas)
        self.ui.hilbert_left_layout.addWidget(self.hilbert_nav_toolbar)

        self.curve_color = "blue"

    def connect_signals(self):
        self.ui.sinh_generate_btn.clicked.connect(self.generate_sinh_fractal)
        self.ui.sinh_save_btn.clicked.connect(lambda: self.save_fractal_image(self.sinh_canvas.fig))
        self.ui.sinh_clear_btn.clicked.connect(self.clear_sinh_scene)

        self.ui.hilbert_generate_btn.clicked.connect(self.generate_hilbert_curve)
        self.ui.hilbert_save_btn.clicked.connect(lambda: self.save_fractal_image(self.hilbert_canvas.fig))
        self.ui.color_btn.clicked.connect(self.select_color)

    def on_mouse_move(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.ui.coords_label.setText(f"X: {x:.4f} Y: {y:.4f}")

    def on_sinh_draw(self, event):
        if not self.ui.adaptive_resolution.isChecked() or not self.fractal_generated:
            return

        xlim = self.sinh_canvas.axes.get_xlim()
        ylim = self.sinh_canvas.axes.get_ylim()

        if (self.current_xlim is not None and self.current_ylim is not None and
                (xlim != self.current_xlim or ylim != self.current_ylim)):
            x_ratio = abs(xlim[1] - xlim[0]) / abs(self.current_xlim[1] - self.current_xlim[0])
            y_ratio = abs(ylim[1] - ylim[0]) / abs(self.current_ylim[1] - self.current_ylim[0])

            if x_ratio < 0.8 or y_ratio < 0.8 or x_ratio > 1.2 or y_ratio > 1.2:
                self.sinh_fractal.x_min, self.sinh_fractal.x_max = xlim
                self.sinh_fractal.y_min, self.sinh_fractal.y_max = ylim

                self.current_xlim = xlim
                self.current_ylim = ylim

                self.generate_sinh_fractal(keep_view=True)

    def generate_sinh_fractal(self, keep_view=False):
        if keep_view:
            xlim = self.sinh_canvas.axes.get_xlim()
            ylim = self.sinh_canvas.axes.get_ylim()

        self.sinh_fractal.width = self.ui.width_input.value()
        self.sinh_fractal.height = self.ui.height_input.value()
        self.sinh_fractal.max_iterations = self.ui.max_iterations_input.value()
        self.sinh_fractal.escape_radius = self.ui.escape_radius_input.value()
        self.sinh_fractal.colormap = self.ui.colormap_combo.currentText()

        c_real = self.ui.c_real_input.value()
        c_imag = self.ui.c_imag_input.value()

        fractal_data = self.sinh_fractal.generate(c_real, c_imag)

        self.sinh_canvas.axes.clear()
        img = self.sinh_canvas.axes.imshow(fractal_data, cmap=self.sinh_fractal.colormap,
                                           extent=[self.sinh_fractal.x_min, self.sinh_fractal.x_max,
                                                   self.sinh_fractal.y_min, self.sinh_fractal.y_max],
                                           origin='lower', aspect='equal')

        self.sinh_canvas.axes.set_title(f"Фрактал sh(z) + c, де c = {c_real} + {c_imag}i")

        self.sinh_canvas.axes.set_xticks([])
        self.sinh_canvas.axes.set_yticks([])

        if keep_view:
            self.sinh_canvas.axes.set_xlim(xlim)
            self.sinh_canvas.axes.set_ylim(ylim)
        else:
            self.current_xlim = self.sinh_canvas.axes.get_xlim()
            self.current_ylim = self.sinh_canvas.axes.get_ylim()

        self.sinh_canvas.fig.tight_layout()
        self.sinh_canvas.draw()

        self.fractal_generated = True

    def clear_sinh_scene(self):
        self.sinh_canvas.axes.clear()
        self.sinh_canvas.fig.tight_layout()
        self.sinh_canvas.draw()

        self.fractal_generated = False

    def generate_hilbert_curve(self):
        self.hilbert_curve.iterations = self.ui.hilbert_iterations_input.value()
        self.hilbert_curve.line_width = self.ui.line_width_input.value()
        self.hilbert_curve.color = self.curve_color

        points = self.hilbert_curve._get_hilbert_points(self.hilbert_curve.iterations)

        self.hilbert_canvas.axes.clear()

        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        self.hilbert_canvas.axes.plot(x_vals, y_vals, color=self.curve_color,
                                      linewidth=self.ui.line_width_input.value())

        self.hilbert_canvas.axes.set_xlim(-0.05, 1.05)
        self.hilbert_canvas.axes.set_ylim(-0.05, 1.05)
        self.hilbert_canvas.axes.set_title(f"Крива Гільберта-Пеано (ітерацій: {self.hilbert_curve.iterations})")
        self.hilbert_canvas.axes.axis('equal')
        self.hilbert_canvas.axes.grid(True, linestyle='--', alpha=0.5)

        self.hilbert_canvas.fig.tight_layout()
        self.hilbert_canvas.draw()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.curve_color = color.name()
            self.ui.color_btn.setStyleSheet(f"background-color: {self.curve_color}")

    def save_fractal_image(self, figure):
        file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти зображення", "",
                                                   "PNG (*.png);;JPEG (*.jpg *.jpeg);;PDF (*.pdf);;SVG (*.svg)")

        if file_path:
            figure.savefig(file_path, dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FractalVisualizerApp()
    window.show()
    sys.exit(app.exec())
