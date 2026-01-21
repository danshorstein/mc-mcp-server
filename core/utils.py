import numpy as np
from PIL import Image

# 21-color Minecraft concrete palette
CONCRETE_PALETTE = {
    'white': (255, 255, 255), 'light_gray': (157, 157, 151), 'gray': (71, 79, 82),
    'black': (16, 16, 16), 'brown': (102, 76, 51), 'red': (153, 51, 51),
    'orange': (216, 127, 51), 'yellow': (229, 229, 51), 'lime': (127, 204, 25),
    'green': (102, 127, 51), 'cyan': (76, 127, 153), 'light_blue': (102, 153, 216),
    'blue': (51, 76, 178), 'purple': (127, 63, 178), 'magenta': (178, 76, 216),
    'pink': (242, 127, 165), 'terracotta': (143, 107, 76),
    'light_gray_terracotta': (135, 107, 98), 'cyan_terracotta': (86, 91, 91),
    'purple_terracotta': (118, 70, 86), 'blue_terracotta': (74, 60, 91),
}

PALETTE_NAMES = list(CONCRETE_PALETTE.keys())
PALETTE_ARRAY = np.array([CONCRETE_PALETTE[name] for name in PALETTE_NAMES], dtype=np.float32)

def find_closest_color_index(rgb):
    rgb = np.array(rgb, dtype=np.float32)
    distances = np.sum((PALETTE_ARRAY - rgb) ** 2, axis=1)
    return np.argmin(distances)

def find_closest_palette_color(rgb):
    idx = find_closest_color_index(rgb)
    return PALETTE_ARRAY[idx]

def rgb_to_concrete(rgb):
    idx = find_closest_color_index(rgb)
    return f"{PALETTE_NAMES[idx]}_concrete"

def is_uniform_region(pixels, y, x, threshold=10):
    h, w = pixels.shape[:2]
    center = pixels[y, x]
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                diff = np.abs(pixels[ny, nx].astype(float) - center.astype(float)).max()
                if diff > threshold: return False
    return True

def apply_floyd_steinberg(pixels, skip_uniform=True):
    h, w = pixels.shape[:2]
    img = pixels.astype(np.float32)
    original = pixels.copy()
    for y in range(h):
        for x in range(w):
            if skip_uniform and is_uniform_region(original, y, x):
                img[y, x] = find_closest_palette_color(img[y, x])
                continue
            old_pixel = img[y, x].copy()
            new_pixel = find_closest_palette_color(old_pixel)
            img[y, x] = new_pixel
            error = old_pixel - new_pixel
            if x + 1 < w: img[y, x + 1] += error * (7 / 16)
            if y + 1 < h:
                if x > 0: img[y + 1, x - 1] += error * (3 / 16)
                img[y + 1, x] += error * (5 / 16)
                if x + 1 < w: img[y + 1, x + 1] += error * (1 / 16)
    return np.clip(img, 0, 255).astype(np.uint8)
