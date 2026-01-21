import unittest
import numpy as np
from core.utils import find_closest_color_index, rgb_to_concrete, apply_floyd_steinberg

class TestUtils(unittest.TestCase):
    def test_find_closest_color_index(self):
        # White should be index 0
        self.assertEqual(find_closest_color_index((255, 255, 255)), 0)
        # Deep blue should be blue
        self.assertEqual(rgb_to_concrete((0, 0, 255)), "blue_concrete")

    def test_rgb_to_concrete(self):
        self.assertEqual(rgb_to_concrete((255, 0, 0)), "red_concrete")
        self.assertEqual(rgb_to_concrete((0, 255, 0)), "lime_concrete")

    def test_dithering_shape(self):
        pixels = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        dithered = apply_floyd_steinberg(pixels)
        self.assertEqual(pixels.shape, dithered.shape)
        self.assertEqual(dithered.dtype, np.uint8)

if __name__ == '__main__':
    unittest.main()
