from mcp.server.fastmcp import FastMCP
from core.minecraft import MinecraftInterface
from core.screen import MinecraftScreen
import os
import math
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("minecraft-overwatch")

# Initialize FastMCP server
mcp = FastMCP("Minecraft Overwatch")

# Initialize Minecraft interface
GDMC_URL = os.environ.get("GDMC_URL", "http://localhost:9000")
mc = MinecraftInterface(GDMC_URL)

@mcp.tool()
def get_player_context():
    """Get the current player's position, rotation, and cardinal facing."""
    logger.info("Fetching player context...")
    info = mc.get_player_info()
    if not info:
        return "Could not connect to Minecraft. Ensure GDMC HTTP is running at " + GDMC_URL
    
    yaw = info['yaw']
    norm_yaw = yaw % 360
    if 315 <= norm_yaw or norm_yaw < 45: facing = "south"
    elif 45 <= norm_yaw < 135: facing = "west"
    elif 135 <= norm_yaw < 225: facing = "north"
    else: facing = "east"
    
    info['facing'] = facing
    logger.info(f"Player context: {info['position']} facing {facing}")
    return info

@mcp.tool()
def place_block(x: int, y: int, z: int, block_type: str):
    """Place a single block at the specified coordinates."""
    logger.info(f"Placing {block_type} at {x}, {y}, {z}")
    success = mc.set_block(x, y, z, block_type)
    return f"Placed {block_type} at {x}, {y}, {z}" if success else f"Failed to place {block_type}."

@mcp.tool()
def fill_area(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block_type: str):
    """Fill a rectangular area with a specific block type."""
    logger.info(f"Filling area from {x1},{y1},{z1} to {x2},{y2},{z2} with {block_type}")
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
    
    logger.info(f"Rendering image {image_path} at ({x}, {y}, {z}) size {size}")
    screen = MinecraftScreen(mc, x, y, z, w, h, facing=facing)
    mc.tellraw(f"Rendering image: {os.path.basename(image_path)} at size {size}...", "gold")
    
    try:
        commands_sent = screen.render_image(image_path)
        if commands_sent > 0:
            mc.tellraw(f"Render complete! ({commands_sent} batches)", "green")
            return f"Successfully rendered {image_path}. Sent {commands_sent} fill commands."
        else:
            return "Render skipped: No changes detected since last render at this location."
    except Exception as e:
        logger.error(f"Render error: {e}")
        return f"Error rendering image: {str(e)}"

@mcp.tool()
def clear_screen(x: int, y: int, z: int, facing: str, size: str = "medium"):
    """Destroy/Clear a screen at the given location and size."""
    sizes = {'small': (128, 72), 'medium': (192, 108), 'large': (256, 144)}
    w, h = sizes.get(size, (192, 108))
    
    logger.info(f"Clearing screen at ({x}, {y}, {z}) size {size}")
    screen = MinecraftScreen(mc, x, y, z, w, h, facing=facing)
    screen.destroy()
    return f"Cleared {size} screen at {x}, {y}, {z}"

@mcp.tool()
def get_build_area():
    """Get the currently defined build area in Minecraft."""
    logger.info("Fetching build area...")
    area = mc.get_build_area()
    return area if area else "No build area defined. Use /setbuildarea in-game."

@mcp.tool()
def get_blocks_in_region(x: int, y: int, z: int, dx: int, dy: int, dz: int):
    """
    Get block types in a rectangular region.
    Returns a string representation of the blocks.
    """
    logger.info(f"Inspecting blocks at {x},{y},{z} size {dx}x{dy}x{dz}")
    blocks = mc.get_blocks(x, y, z, dx, dy, dz)
    return blocks if blocks else "Failed to retrieve block data."

@mcp.tool()
def get_world_state():
    """Get information about the Minecraft world (time, weather, etc.)."""
    logger.info("Fetching world state...")
    state = mc.get_world_info()
    return state

@mcp.tool()
def run_minecraft_command(command: str):
    """
    Execute any raw Minecraft command. 
    Use this for complex actions not covered by other tools (e.g., gamerules, advanced summoning).
    """
    logger.info(f"Running raw command: {command}")
    return mc.execute_command(command)

@mcp.tool()
def spawn_entities(entity_type: str, x: int, y: int, z: int, count: int = 1, nbt: str = ""):
    """
    Spawn one or more entities at a location.
    Example: spawn_entities("zombie", 100, 64, 100, count=5)
    """
    logger.info(f"Spawning {count} {entity_type} at {x}, {y}, {z}")
    results = []
    for _ in range(count):
        success = mc.spawn_entity(entity_type, x, y, z, nbt)
        results.append(success)
    
    success_count = sum(results)
    return f"Successfully spawned {success_count}/{count} {entity_type}."

@mcp.tool()
def control_world(feature: str, value: str):
    """
    Control world-wide features.
    Features: 'weather' (clear/rain/thunder), 'time' (day/night/number), 'gamerule' (rule value).
    """
    logger.info(f"Setting world {feature} to {value}")
    success = mc.set_world_property(feature, value)
    return f"World {feature} set to {value}." if success else f"Failed to set {feature}."

@mcp.tool()
def place_command_block(x: int, y: int, z: int, command: str, mode: str = "impulse", facing: str = "north", always_active: bool = False):
    """
    Place a command block with a script.
    - x, y, z: Coordinates
    - command: The Minecraft command/script to run
    - mode: 'impulse' (orange), 'repeating' (purple), 'chain' (teal)
    - facing: 'north', 'south', 'east', 'west', 'up', 'down'
    - always_active: If true, runs without redstone
    """
    logger.info(f"Placing {mode} command block at {x},{y},{z} (auto={always_active})")
    success = mc.set_command_block(x, y, z, command, mode, facing, auto=always_active)
    return f"Placed {mode} command block at {x}, {y}, {z}" if success else "Failed to place command block."

if __name__ == "__main__":
    mcp.run()

