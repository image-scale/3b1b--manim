"""Color manipulation utilities."""
import numpy as np
from colour import Color


def hex_to_rgb(hex_code):
    """Convert a hex color code to RGB values in range [0, 1]."""
    # Remove # if present
    hex_code = hex_code.lstrip('#')
    # Convert hex to RGB
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return np.array([r, g, b])


def rgb_to_hex(rgb):
    """Convert RGB values (0-1 range) to hex color code."""
    r = int(round(rgb[0] * 255))
    g = int(round(rgb[1] * 255))
    b = int(round(rgb[2] * 255))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def color_to_rgb(color):
    """Convert a color (string or Color object) to RGB array in range [0, 1]."""
    if isinstance(color, Color):
        return np.array(color.get_rgb())
    # Assume it's a hex string
    return hex_to_rgb(color)


def color_to_rgba(color, alpha=1.0):
    """Convert a color to RGBA array with optional alpha."""
    rgb = color_to_rgb(color)
    return np.array([rgb[0], rgb[1], rgb[2], alpha])


def rgb_to_color(rgb):
    """Convert RGB values (0-1 range) to a Color object."""
    c = Color()
    c.set_rgb(tuple(rgb))
    return c


def rgba_to_color(rgba):
    """Convert RGBA values to a Color object (ignoring alpha)."""
    return rgb_to_color(rgba[:3])


def invert_color(color):
    """Invert a color (1 - each RGB component)."""
    rgb = color_to_rgb(color)
    inverted_rgb = 1.0 - rgb
    return rgb_to_color(inverted_rgb)


def color_to_int_rgb(color):
    """Convert a color to integer RGB values (0-255 range)."""
    rgb = color_to_rgb(color)
    return np.array([
        int(round(rgb[0] * 255)),
        int(round(rgb[1] * 255)),
        int(round(rgb[2] * 255))
    ])
