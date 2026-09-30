"""Device silhouettes for the retained Tk placement guide."""

from __future__ import annotations


def draw_flipper(canvas, x, y, back=False):
    def box(left, top, right, bottom, **style):
        canvas.create_rectangle(x + left, y + top, x + right, y + bottom, **style)

    points = (12, 12, 100, 12, 109, 22, 109, 42, 100, 52, 12, 52, 3, 42, 3, 22)
    canvas.create_polygon(
        *[x + value if i % 2 == 0 else y + value for i, value in enumerate(points)],
        smooth=True, fill="#FFFCF7", outline="#344054", width=2,
    )
    box(3, 24, 8, 40, fill="#344054", outline="")
    if back:
        for radius in (5, 9, 13):
            canvas.create_oval(x + 56 - radius, y + 32 - radius,
                               x + 56 + radius, y + 32 + radius,
                               outline="#F69B43", width=2)
    else:
        box(16, 20, 65, 44, fill="#F6BC77", outline="#F69B43", width=2)
        box(20, 24, 61, 40, fill="#E3EDD1", outline="#344054")
        box(29, 30, 47, 34, fill="#344054", outline="")
        box(76, 22, 99, 43, fill="#F69B43", outline="#CB752B")
        box(85, 25, 90, 40, fill="#FFFCF7", outline="")
        box(80, 30, 95, 35, fill="#FFFCF7", outline="")


def draw_tamagotchi(canvas, x, y, palette, back=False, sideways=False):
    def point(px, py):
        return (x + 64 - py, y + px) if sideways else (x + px, y + py)

    def polygon(points, **style):
        canvas.create_polygon(*[coordinate for p in points for coordinate in point(*p)], **style)

    def box(left, top, right, bottom, **style):
        polygon(((left, top), (right, top), (right, bottom), (left, bottom)), **style)

    polygon(((32, 4), (46, 12), (57, 35), (57, 48), (47, 60),
             (17, 60), (7, 48), (7, 35), (18, 12)),
            smooth=True, fill=palette["card"], outline=palette["accent"], width=2)
    box(27, 3, 37, 8, fill="#344054", outline="")
    if back:
        box(19, 23, 45, 51, fill=palette["card"], outline=palette["accent"], width=2)
    else:
        box(16, 23, 48, 45, fill="#E3EDD1", outline=palette["accent"], width=2)
        box(25, 31, 28, 34, fill="#344054", outline="")
        box(36, 31, 39, 34, fill="#344054", outline="")
        box(29, 37, 35, 39, fill="#344054", outline="")
        for center in (22, 32, 42):
            cx, cy = point(center, 52)
            canvas.create_oval(cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6,
                               fill=palette["accent"], outline="")
