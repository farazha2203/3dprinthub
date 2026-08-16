from __future__ import annotations

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk


class IconRegistry:
    """Small DPI-safe icon set rendered locally; no font/emoji dependency."""

    def __init__(self, master, size: int = 20):
        self.master = master
        self.size = int(size)
        self._cache: dict[tuple[str, str], ImageTk.PhotoImage] = {}

    def get(self, name: str, color: str = "#d9e4ee"):
        key = (name, color)
        if key not in self._cache:
            self._cache[key] = ImageTk.PhotoImage(self._draw(name, color), master=self.master)
        return self._cache[key]

    def _draw(self, name: str, color: str) -> Image.Image:
        s = self.size
        image = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        w = max(1, s // 9)
        p = max(2, s // 6)
        c = color

        if name == "dashboard":
            q = (s - p * 2 - 2) // 2
            for x, y in ((p, p), (p + q + 2, p), (p, p + q + 2), (p + q + 2, p + q + 2)):
                draw.rounded_rectangle((x, y, x + q, y + q), radius=2, outline=c, width=w)
        elif name == "products":
            draw.rectangle((p, p + 2, s - p, s - p), outline=c, width=w)
            draw.line((p, p + 2, s // 2, p - 1, s - p, p + 2), fill=c, width=w)
            draw.line((s // 2, p - 1, s // 2, s - p), fill=c, width=w)
        elif name == "discover":
            r = s // 4
            cx, cy = s // 2 - 2, s // 2 - 2
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=w)
            draw.line((cx + r - 1, cy + r - 1, s - p, s - p), fill=c, width=w + 1)
        elif name == "publish":
            draw.line((s // 2, s - p, s // 2, p + 2), fill=c, width=w + 1)
            draw.line((s // 2, p + 1, p + 2, s // 2), fill=c, width=w + 1)
            draw.line((s // 2, p + 1, s - p - 2, s // 2), fill=c, width=w + 1)
            draw.line((p, s - p, s - p, s - p), fill=c, width=w)
        elif name == "published":
            draw.ellipse((p, p, s - p, s - p), outline=c, width=w)
            draw.line((p + 4, s // 2, s // 2 - 1, s - p - 4, s - p - 2, p + 4), fill=c, width=w + 1)
        elif name == "blocked":
            draw.ellipse((p, p, s - p, s - p), outline=c, width=w)
            draw.line((p + 3, s - p - 3, s - p - 3, p + 3), fill=c, width=w + 1)
        elif name == "logs":
            for y in (p + 2, s // 2, s - p - 2):
                draw.ellipse((p, y - 1, p + 2, y + 1), fill=c)
                draw.line((p + 5, y, s - p, y), fill=c, width=w)
        elif name == "ai":
            cx = cy = s // 2
            pts = [(cx, p), (cx + 2, cy - 2), (s - p, cy), (cx + 2, cy + 2), (cx, s - p), (cx - 2, cy + 2), (p, cy), (cx - 2, cy - 2)]
            draw.polygon(pts, outline=c)
            draw.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill=c)
        elif name == "connection":
            draw.arc((p, p + 2, s // 2 + 3, s - p - 2), 280, 80, fill=c, width=w)
            draw.arc((s // 2 - 3, p + 2, s - p, s - p - 2), 100, 260, fill=c, width=w)
            draw.line((s // 2 - 4, s // 2, s // 2 + 4, s // 2), fill=c, width=w)
        elif name == "settings":
            cx = cy = s // 2
            r = s // 4
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=w)
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), outline=c, width=w)
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                x1 = cx + dx * (r + 1); y1 = cy + dy * (r + 1)
                x2 = cx + dx * (r + 5); y2 = cy + dy * (r + 5)
                draw.line((x1, y1, x2, y2), fill=c, width=w)
        else:
            draw.rounded_rectangle((p, p, s - p, s - p), radius=3, outline=c, width=w)
        return image
