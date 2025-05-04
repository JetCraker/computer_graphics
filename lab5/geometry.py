import numpy as np
import math


def get_translation_matrix(tx, ty):
    """Повертає матрицю переміщення 3x3 в однорідних координатах."""
    return np.array([
      [1, 0, tx],
      [0, 1, ty],
      [0, 0, 1]
    ], dtype=float)


def get_scaling_matrix(sx, sy):
    """Повертає матрицю масштабування 3x3 відносно (0,0)."""
    return np.array([
      [sx, 0, 0],
      [0, sy, 0],
      [0, 0, 1]
    ], dtype=float)


def get_scaling_matrix_around_point(sx, sy, cx, cy):
    """Повертає матрицю масштабування 3x3 відносно точки (cx, cy)."""
    to_origin = get_translation_matrix(-cx, -cy)
    scale = get_scaling_matrix(sx, sy)
    from_origin = get_translation_matrix(cx, cy)
    return from_origin @ scale @ to_origin


def get_rotation_matrix(theta_radians):
    """Повертає матрицю обертання 3x3 навколо (0,0) на кут theta (в радіанах)."""
    cos_t = math.cos(theta_radians)
    sin_t = math.sin(theta_radians)
    return np.array([
      [cos_t, -sin_t, 0],
      [sin_t,  cos_t, 0],
      [0,      0,     1]
    ], dtype=float)


def get_rotation_matrix_around_point(theta_radians, cx, cy):
    """Повертає матрицю обертання 3x3 навколо точки (cx, cy) на кут theta (в радіанах)."""
    to_origin = get_translation_matrix(-cx, -cy)
    rotate = get_rotation_matrix(theta_radians)
    from_origin = get_translation_matrix(cx, cy)
    return from_origin @ rotate @ to_origin


def apply_transform(vertices, matrix):
    """
    Застосовує матрицю перетворення до вершин.
    vertices: numpy array (N, 2) - координати вершин (x, y)
    matrix: numpy array (3, 3) - матриця перетворення
    Повертає: numpy array (N, 2) - нові координати вершин
    """
    n_vertices = vertices.shape[0]
    # Перетворення в однорідні координати (додаємо 1)
    # Створюємо масив (N, 3) з одиницями в останньому стовпці
    homogeneous_coords = np.hstack([vertices[:, :2], np.ones((n_vertices, 1))])

    # Транспонуємо для множення: (3, N)
    homogeneous_coords_T = homogeneous_coords.T

    # Застосовуємо матрицю: M (3,3) @ Vert_T (3,N) -> New_Vert_T (3,N)
    transformed_coords_T = matrix @ homogeneous_coords_T

    # Транспонуємо назад: (N, 3)
    transformed_coords = transformed_coords_T.T

    # Повертаємо до 2D координат (ігноруємо третю координату, оскільки w=1 для афінних)
    return transformed_coords[:, :2]


def get_centroid(vertices):
    """Обчислює центр мас (центроїд) фігури."""
    return np.mean(vertices[:, :2], axis=0)


class Trapezoid:
    def __init__(self, vertices):
        if not isinstance(vertices, np.ndarray):
            vertices = np.array(vertices, dtype=float)
        if vertices.shape != (4, 2):
             if vertices.ndim == 2 and vertices.shape[0] == 4 and vertices.shape[1] > 2:
                 vertices = vertices[:, :2] # Take only first two columns
             else:
                 raise ValueError(f"Трапеція повинна мати 4 вершини з координатами (x, y). Отримано форму: {vertices.shape}")
        self.initial_vertices = vertices.copy() # Зберігаємо початкові
        self.current_vertices = vertices.copy()

    def transform(self, matrix):
        """Трансформує поточні вершини трапеції."""
        self.current_vertices = apply_transform(self.current_vertices, matrix)

    def reset(self):
        """Повертає трапецію до початкового стану."""
        self.current_vertices = self.initial_vertices.copy()
