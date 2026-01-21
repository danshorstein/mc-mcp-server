import os
import time
import json
import numpy as np
import logging
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageEnhance
from .utils import apply_floyd_steinberg, rgb_to_concrete

logger = logging.getLogger(__name__)

class MinecraftScreen:
    def __init__(self, interface: Any, origin_x: int, origin_y: int, origin_z: int, width: int, height: int, facing: str = 'north'):
        self.mc = interface
        self.origin = (origin_x, origin_y, origin_z)
        self.width = width
        self.height = height
        self.facing = facing  # 'north', 'south', 'east', 'west'
        
        # Create state directory
        self.state_dir = '.state'
        os.makedirs(self.state_dir, exist_ok=True)
        
        # Unique state file name based on location and facing
        Safe_name = f"screen_{origin_x}_{origin_y}_{origin_z}_{facing}.json"
        self.state_file = os.path.join(self.state_dir, Safe_name)
        
    def get_coords(self, x: int, y: int) -> Tuple[int, int, int]:
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

    def render_image(self, image_path: str, use_dithering: bool = True, smart_diff: bool = True) -> int:
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")

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
            try:
                with open(self.state_file, 'r') as f:
                    old_state = json.load(f)
                blocks_to_update = {k: v for k, v in new_blocks.items() if old_state.get(k) != v}
            except Exception as e:
                logger.warning(f"Could not load old state from {self.state_file}: {e}")
        
        if not blocks_to_update:
            logger.info("No changes detected, skipping render.")
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
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(new_blocks, f)
        except Exception as e:
            logger.error(f"Could not save state to {self.state_file}: {e}")
            
        return sent

    def destroy(self) -> None:
        x1, y1, z1 = self.get_coords(0, 0)
        x2, y2, z2 = self.get_coords(self.width - 1, self.height - 1)
        self.mc.fill_region(x1, y1, z1, x2, y2, z2, 'air')
        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
            except Exception as e:
                logger.error(f"Could not delete state file {self.state_file}: {e}")

