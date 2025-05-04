import numpy as np


def save_matrix(matrix, filename):
    """Зберігає NumPy матрицю у текстовий файл."""
    try:
        import datetime
        np.savetxt(filename, matrix, fmt='%.4f', header=f'Матриця перетворення (збережено: {datetime.datetime.now()})')
    except Exception as e:
        print(f"Помилка збереження матриці у файл '{filename}': {e}")
        raise


def save_vertices(vertices, filename):
    """Зберігає координати вершин у текстовий файл."""
    try:
        import datetime
        np.savetxt(filename, vertices, fmt='%.4f', header=f'Початкові координати вершин (збережено: {datetime.datetime.now()})')
    except Exception as e:
        print(f"Помилка збереження вершин у файл '{filename}': {e}")
        raise
