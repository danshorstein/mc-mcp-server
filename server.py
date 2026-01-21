from mcp.server.fastmcp import FastMCP
from core.minecraft import MinecraftInterface
from core.screen import MinecraftScreen
import os
import math

# Initialize FastMCP server
mcp = FastMCP("Minecraft Overwatch")

# Initialize Minecraft interface
GDMC_URL = os.environ.get("GDMC_URL", "http://localhost:9000")
mc = MinecraftInterface(GDMC_URL)

@mcp.tool()
def get_player_context():
    """Get the current player's position, rotation, and cardinal facing."""
    info = mc.get_player_info()
    if not info:
        return "Could not connect to Minecraft. Ensure GDMC HTTP is running."
    
    yaw = info['yaw']
    norm_yaw = yaw % 360
    if 315 <= norm_yaw or norm_yaw < 45: facing = "south"
    elif 45 <= norm_yaw < 135: facing = "west"
    elif 135 <= norm_yaw < 225: facing = "north"
    else: facing = "east"
    
    info['facing'] = facing
    return info

@mcp.tool()
def place_block(x: int, y: int, z: int, block_type: str):
    """Place a single block at the specified coordinates."""
    success = mc.set_block(x, y, z, block_type)
    return f"Placed {block_type} at {x}, {y}, {z}" if success else "Failed to place block."

@mcp.tool()
def fill_area(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block_type: str):
    """Fill a rectangular area with a specific block type."""
    success = mc.fill_region(x1, y1, z1, x2, y2, z2, block_type)
    return f"Filled area with {block_type}" if success else "Failed to fill area."

@mcp.tool()
def render_image_to_screen(image_path: str, x: int, y: int, z: int, facing: str, size: str = "medium"):
    """
    Render an image file to a Minecraft screen.
    Provide the anchor (bottom-left) coordinates and cardinal facing (north/south/east/west).
    Sizes: small (128x72), medium (192x108), large (256x144)
    """
    sizes = {'small': (128, 72), 'medium': (192, 108), 'large': (256, 144)}
    w, h = sizes.get(size, (192, 108))
    
    screen = MinecraftScreen(mc, x, y, z, w, h, facing=facing)
    mc.tellraw(f"Rendering image: {os.path.basename(image_path)} at size {size}...", "gold")
    
    try:
        commands_sent = screen.render_image(image_path)
        mc.tellraw(f"Render complete! ({commands_sent} batches)", "green")
        return f"Successfully rendered {image_path}. Sent {commands_sent} fill commands."
    except Exception as e:
        return f"Error rendering image: {str(e)}"

@mcp.tool()
def clear_screen(x: int, y: int, z: int, facing: str, size: str = "medium"):
    """Destroy/Clear a screen at the given location and size."""
    sizes = {'small': (128, 72), 'medium': (192, 108), 'large': (256, 144)}
    w, h = sizes.get(size, (192, 108))
    
    screen = MinecraftScreen(mc, x, y, z, w, h, facing=facing)
    screen.destroy()
    return f"Cleared {size} screen at {x}, {y}, {z}"

if __name__ == "__main__":
    mcp.run()
