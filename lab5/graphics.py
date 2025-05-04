import pygame
import config

try:
    pygame.font.init()
    font = pygame.font.SysFont(None, config.FONT_SIZE)
except Exception as e:
    print(f"Помилка ініціалізації шрифтів: {e}")

    class DummyFont:
        def render(self, *args, **kwargs):
            return pygame.Surface((0,0))
    font = DummyFont()


if pygame.font:
    try:
        pygame.font.init()
        font = pygame.font.SysFont(None, config.FONT_SIZE)
    except Exception as e:
        print(f"Помилка ініціалізації шрифтів: {e}")
        class DummyFont:
            def render(self, *args, **kwargs):
                return pygame.Surface((0,0))
            def get_height(self):
                return 10
        font = DummyFont()


def draw_text(screen, text, position, color=config.BLACK, text_font=None):
    """Малює текст на екрані."""
    if text_font is None:
        text_font = font
    try:
        text_surface = text_font.render(text, True, color)
        screen.blit(text_surface, position)
    except Exception as e:
        print(f"Помилка малювання тексту '{text}': {e}")


def draw_coordinate_plane(screen, center_x, center_y, width, height, zoom, grid_color, axis_color):
    """Малює координатні осі, сітку та підписи."""

    step = config.GRID_STEP * zoom
    if step < 5:
        step = (config.GRID_STEP * 5) * zoom
        if step < 5: step = (config.GRID_STEP * 10) * zoom
        if step < 5: step = 5

    x = center_x % step
    while x < width:
        pygame.draw.line(screen, grid_color, (int(x), 0), (int(x), height))
        x += step

    y = center_y % step
    while y < height:
        pygame.draw.line(screen, grid_color, (0, int(y)), (width, int(y)))
        y += step

    pygame.draw.line(screen, axis_color, (0, center_y), (width, center_y), 2) # Вісь X
    pygame.draw.line(screen, axis_color, (center_x, 0), (center_x, height), 2) # Вісь Y

    unit_x = -center_x // zoom -1
    while (coord_x := center_x + unit_x * zoom) < width:
        if abs(coord_x - center_x) > zoom / 4:
           screen_x = int(coord_x)
           pygame.draw.line(screen, axis_color, (screen_x, center_y - 5), (screen_x, center_y + 5), 1)
           if unit_x != 0:
                label = font.render(str(int(unit_x)), True, config.LABEL_COLOR)
                screen.blit(label, (screen_x - label.get_width() // 2, center_y + 8))
        unit_x += 1

    unit_y = (height - center_y) // zoom + 1
    while (coord_y := center_y - unit_y * zoom) < height:
         if abs(coord_y - center_y) > zoom / 4:
            screen_y = int(coord_y)
            pygame.draw.line(screen, axis_color, (center_x - 5, screen_y), (center_x + 5, screen_y), 1)
            if unit_y != 0:
                label = font.render(str(int(unit_y)), True, config.LABEL_COLOR)
                screen.blit(label, (center_x - label.get_width() - 8, screen_y - label.get_height() // 2))
         unit_y -= 1

    label_x = font.render("X", True, config.LABEL_COLOR)
    screen.blit(label_x, (width - label_x.get_width() - 5, center_y - label_x.get_height() - 5))
    label_y = font.render("Y", True, config.LABEL_COLOR)
    screen.blit(label_y, (center_x + 5, 5))
    label_0 = font.render("0", True, config.LABEL_COLOR)
    screen.blit(label_0, (center_x + 5, center_y + 5))


def draw_trapezoid(screen, trapezoid, center_x, center_y, zoom, color):
    """Малює трапецію на екрані."""
    screen_vertices = trapezoid.get_vertices_for_drawing(config.SCREEN_HEIGHT, center_x, center_y, zoom)

    if len(screen_vertices) == 4:
        pygame.draw.polygon(screen, color, screen_vertices, 0)
        pygame.draw.polygon(screen, config.BLACK, screen_vertices, 1)
