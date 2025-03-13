import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from graph import Ui_MainWindow


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

        self.ui.CreateButton.clicked.connect(self.create_triangle)
        self.ui.ClearButton.clicked.connect(self.clear)

        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

    def create_triangle(self):
        try:
            x1 = int(self.ui.X1_lineEdit.text())
            y1 = int(self.ui.Y1_lineEdit.text())
            x2 = int(self.ui.X2_lineEdit.text())
            y2 = int(self.ui.Y2_lineEdit.text())
            color = self.ui.Color_lineEdit.text()

            # Обчислюємо координати третьої вершини рівностороннього трикутника
            x3 = x1 + (x2 - x1) * math.cos(math.radians(60)) - (y2 - y1) * math.sin(math.radians(60))
            y3 = y1 + (x2 - x1) * math.sin(math.radians(60)) + (y2 - y1) * math.cos(math.radians(60))

            x = [x1, x2, x3, x1]
            y = [y1, y2, y3, y1]

            self.ax.axhline(0, color="black", linewidth=1)
            self.ax.axvline(0, color="black", linewidth=1)

            if self.ui.comboBox.currentText() == "Without anything":
                self.ax.plot(x, y, linestyle='-', color=color, label='Трикутник')
            elif self.ui.comboBox.currentText() == "Circles":
                self.ax.plot(x, y, marker="o", linestyle='-', color=color, label='Трикутник')
            elif self.ui.comboBox.currentText() == "Squares":
                self.ax.plot(x, y, marker="s", linestyle='-', color=color, label='Трикутник')

            self.ax.fill(x, y, facecolor=color, edgecolor=color)

            self.ax.set_xlim(min(x) - 1, max(x) + 1)
            self.ax.set_ylim(min(y) - 1, max(y) + 1)
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Y")
            self.ax.grid(True)
            self.ax.legend()

            self.canvas.draw()
        except ValueError:
            self.ui.error_label.setText("Дані введені некоректно!")

    def clear(self):
        self.ax.clear()
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes:
            print(f"Клік: ({event.xdata:.2f}, {event.ydata:.2f})")

    def on_scroll(self, event):
        scale_factor = 1.2 if event.step > 0 else 0.8
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_mid = (xlim[0] + xlim[1]) / 2
        y_mid = (ylim[0] + ylim[1]) / 2

        self.ax.set_xlim([x_mid + (x - x_mid) * scale_factor for x in xlim])
        self.ax.set_ylim([y_mid + (y - y_mid) * scale_factor for y in ylim])
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TriangleAPP()
    window.show()
    sys.exit(app.exec())
