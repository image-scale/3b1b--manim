import numpy as np
import random


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3:
        hex_code = ''.join(c * 2 for c in hex_code)
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return np.array([r, g, b], dtype=float)


def color_to_rgb(color):
    if isinstance(color, str):
        return hex_to_rgb(color)
    if isinstance(color, (list, tuple, np.ndarray)):
        arr = np.array(color, dtype=float)
        if len(arr) >= 3:
            return arr[:3]
    return np.array([1.0, 1.0, 1.0])


def color_to_rgba(color, alpha=1.0):
    rgb = color_to_rgb(color)
    return np.array([rgb[0], rgb[1], rgb[2], alpha], dtype=float)


def rgb_to_hex(rgb):
    rgb = np.array(rgb, dtype=float)
    rgb = np.clip(rgb, 0, 1)
    r = int(round(rgb[0] * 255))
    g = int(round(rgb[1] * 255))
    b = int(round(rgb[2] * 255))
    return f"#{r:02X}{g:02X}{b:02X}"


def rgba_to_hex(rgba):
    return rgb_to_hex(rgba[:3])


def color_to_int_rgb(color):
    rgb = color_to_rgb(color)
    return (rgb * 255).astype(np.uint8)


def color_to_int_rgba(color, opacity=1.0):
    rgba = color_to_rgba(color, opacity)
    return (rgba * 255).astype(np.uint8)


def color_to_hex(color):
    return rgb_to_hex(color_to_rgb(color))


def invert_color(color):
    rgb = color_to_rgb(color)
    return rgb_to_hex(1.0 - rgb)


def interpolate_color(color1, color2, alpha):
    rgb1 = color_to_rgb(color1)
    rgb2 = color_to_rgb(color2)
    blended = np.sqrt((1 - alpha) * rgb1 ** 2 + alpha * rgb2 ** 2)
    return rgb_to_hex(blended)


def color_gradient(reference_colors, length_of_output):
    if length_of_output == 0:
        return []
    if length_of_output == 1:
        return [reference_colors[0] if reference_colors else "#FFFFFF"]
    if len(reference_colors) == 0:
        return ["#FFFFFF"] * length_of_output
    if len(reference_colors) == 1:
        return [reference_colors[0]] * length_of_output

    n_refs = len(reference_colors)
    result = []
    for i in range(length_of_output):
        alpha = i / (length_of_output - 1)
        scaled = alpha * (n_refs - 1)
        lower = int(scaled)
        upper = min(lower + 1, n_refs - 1)
        frac = scaled - lower
        result.append(interpolate_color(reference_colors[lower], reference_colors[upper], frac))
    return result


def average_color(*colors):
    if not colors:
        return "#FFFFFF"
    rgbs = np.array([color_to_rgb(c) for c in colors])
    avg = np.sqrt(np.mean(rgbs ** 2, axis=0))
    return rgb_to_hex(avg)


def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return rgb_to_hex(np.array([r, g, b]))


def random_bright_color():
    h = random.random()
    s = 0.5 + random.random() * 0.3
    l = 0.5 + random.random() * 0.5
    return rgb_to_hex(_hsl_to_rgb(h, s, l))


def _hsl_to_rgb(h, s, l):
    if s == 0:
        return np.array([l, l, l])
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1 / 3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1 / 3)
    return np.array([r, g, b])
