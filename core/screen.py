import os
import time
import json
import numpy as np
from PIL import Image, ImageEnhance
from .utils import apply_floyd_steinberg, rgb_to_concrete

class MinecraftScreen:
    def __init__(self, interface, origin_x, origin_y, origin_z, width, height, facing='north'):
        self.mc = interface
        self.origin = (origin_x, origin_y, origin_z)
        self.width = width
        self.height = height
        self.facing = facing  # 'north', 'south', 'east', 'west'
        self.state_file = 'screen_state.json'
        
    def get_coords(self, x, y):
        """Map image x, y to Minecraft coordinates based on facing."""
        ox, oy, oz = self.origin
        my = oy + y
        
        if self.facing == 'north':
            return ox + x, my, oz
        elif self.facing == 'south':
            return ox - x, my, oz
        elif self.facing == 'east':
            return ox, my, oz - x
        elif self.facing == 'west':
            return ox, my, oz + x
        return ox + x, my, oz

    def render_image(self, image_path, use_dithering=True, smart_diff=True):
        img = Image.open(image_path).convert('RGB')
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        pixels = np.array(img)
        
        if use_dithering:
            pixels = apply_floyd_steinberg(pixels)
        
        new_blocks = {}
        for y in range(self.height):
            for x in range(self.width):
                rgb = tuple(pixels[y, x])
                block_type = rgb_to_concrete(rgb)
                # Minecraft Y is up
                my_offset = self.height - 1 - y
                mx, my, mz = self.get_coords(x, my_offset)
                new_blocks[f"{mx},{my},{mz}"] = block_type
        
        blocks_to_update = new_blocks
        if smart_diff and os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                old_state = json.load(f)
            blocks_to_update = {k: v for k, v in new_blocks.items() if old_state.get(k) != v}
        
        if not blocks_to_update:
            return 0

        # Horizontal batching
        sent = 0
        for y_img in range(self.height):
            x_img = 0
            while x_img < self.width:
                my_offset = self.height - 1 - y_img
                mx, my, mz = self.get_coords(x_img, my_offset)
                key = f"{mx},{my},{mz}"
                
                if key not in blocks_to_update:
                    x_img += 1
                    continue
                    
                block_type = blocks_to_update[key]
                run_start_x = x_img
                while x_img < self.width:
                    nmx, nmy, nmz = self.get_coords(x_img, my_offset)
                    if blocks_to_update.get(f"{nmx},{nmy},{nmz}") != block_type:
                        break
                    x_img += 1
                
                run_end_x = x_img - 1
                ax1, ay1, az1 = self.get_coords(run_start_x, my_offset)
                ax2, ay2, az2 = self.get_coords(run_end_x, my_offset)
                self.mc.fill_region(ax1, ay1, az1, ax2, ay2, az2, block_type)
                sent += 1
        
        with open(self.state_file, 'w') as f:
            json.dump(new_blocks, f)
            
        return sent

    def destroy(self):
        x1, y1, z1 = self.get_coords(0, 0)
        x2, y2, z2 = self.get_coords(self.width - 1, self.height - 1)
        self.mc.fill_region(x1, y1, z1, x2, y2, z2, 'air')
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
