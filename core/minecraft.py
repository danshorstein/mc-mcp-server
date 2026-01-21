import requests
import re
import math
import json
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class MinecraftInterface:
    def __init__(self, base_url: str = 'http://localhost:9000'):
        self.base_url = base_url

    def send_command(self, command: str) -> bool:
        """Send a command to Minecraft via GDMC HTTP."""
        try:
            url = f'{self.base_url}/command'
            response = requests.post(url, data=command, timeout=5)
            if response.status_code != 200:
                logger.error(f"Command failed with status {response.status_code}: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Command error: {e}")
            return False

    def get_player_info(self) -> Optional[Dict[str, Any]]:
        """Get current player position and rotation."""
        try:
            # Get position via data command
            pos_resp = requests.post(f'{self.base_url}/command', data='data get entity @p Pos')
            rot_resp = requests.post(f'{self.base_url}/command', data='data get entity @p Rotation')
            
            if pos_resp.status_code == 200 and rot_resp.status_code == 200:
                pos_data = pos_resp.json()
                rot_data = rot_resp.json()
                
                # Parse position: [159.81d, 136.47d, 320.27d]
                pos_match = re.search(r'\[([-\d.]+)d?, ([-\d.]+)d?, ([-\d.]+)d?\]', pos_data[0]['message'])
                rot_match = re.search(r'\[([-\d.]+)f?, ([-\d.]+)f?\]', rot_data[0]['message'])
                
                if pos_match and rot_match:
                    pos = (int(float(pos_match.group(1))), 
                           int(float(pos_match.group(2))), 
                           int(float(pos_match.group(3))))
                    yaw = float(rot_match.group(1))
                    pitch = float(rot_match.group(2))
                    return {'position': pos, 'yaw': yaw, 'pitch': pitch}
                else:
                    logger.warning(f"Could not parse player info from response. Pos: {pos_data}, Rot: {rot_data}")
        except Exception as e:
            logger.error(f"Could not get player info: {e}")
        return None

    def fill_region(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block_type: str) -> bool:
        """Execute a /fill command."""
        if not block_type.startswith("minecraft:"):
            block_type = f"minecraft:{block_type}"
        command = f'fill {int(x1)} {int(y1)} {int(z1)} {int(x2)} {int(y2)} {int(z2)} {block_type}'
        return self.send_command(command)

    def set_block(self, x: int, y: int, z: int, block_type: str) -> bool:
        """Execute a /setblock command."""
        if not block_type.startswith("minecraft:"):
            block_type = f"minecraft:{block_type}"
        command = f'setblock {int(x)} {int(y)} {int(z)} {block_type}'
        return self.send_command(command)

    def tellraw(self, message: str, color: str = "white") -> bool:
        """Send a tellraw message to all players."""
        payload = json.dumps([
            "",
            {"text": "🤖 [MCP] ", "color": "aqua", "bold": True},
            {"text": message, "color": color}
        ])
        return self.send_command(f'tellraw @a {payload}')

    def get_build_area(self) -> Optional[Dict[str, Any]]:
        """Get the defined build area from GDMC."""
        try:
            response = requests.get(f'{self.base_url}/buildarea', timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Could not get build area: {e}")
        return None

    def get_blocks(self, x: int, y: int, z: int, dx: int, dy: int, dz: int) -> Optional[str]:
        """Get block data for a region as a string (block types)."""
        try:
            url = f'{self.base_url}/chunks?x={x}&y={y}&z={z}&dx={dx}&dy={dy}&dz={dz}'
            response = requests.get(url, headers={'Accept': 'text/plain'}, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.error(f"Could not get blocks: {e}")
        return None

    def get_world_info(self) -> Dict[str, Any]:
        """Get world-wide information like time and weather."""
        info = {}
        try:
            # Get time
            time_resp = requests.post(f'{self.base_url}/command', data='time query daytime')
            if time_resp.status_code == 200:
                info['daytime'] = time_resp.json()[0]['message']
            
            # Get weather - we iterate through common weather states
            info['weather'] = "Check in-game (feature limited by GDMC command response parsing)"
        except Exception as e:
            logger.error(f"Could not get world info: {e}")
        return info

    def execute_command(self, command: str) -> str:
        """Execute a raw Minecraft command and return the response message."""
        try:
            url = f'{self.base_url}/command'
            response = requests.post(url, data=command, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data[0]['message'] if data else "Command executed."
            return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return f"Exception: {str(e)}"

    def spawn_entity(self, entity_type: str, x: int, y: int, z: int, nbt: Optional[str] = None) -> bool:
        """Spawn an entity at the specified coordinates."""
        nbt_str = nbt if nbt else ""
        command = f'summon {entity_type} {x} {y} {z} {nbt_str}'.strip()
        return self.send_command(command)

    def set_world_property(self, property_type: str, value: str) -> bool:
        """Set a world property like weather, time, or gamerule."""
        if property_type == "weather":
            command = f'weather {value}'
        elif property_type == "time":
            command = f'time set {value}'
        elif property_type == "gamerule":
            command = f'gamerule {value}'
        else:
            command = f'{property_type} {value}'
        return self.send_command(command)

    def set_command_block(self, x: int, y: int, z: int, command_to_run: str, mode: str = "impulse", facing: str = "north", conditional: bool = False, auto: bool = False) -> bool:
        """
        Place and configure a command block.
        Modes: impulse, repeating, chain
        Facings: north, south, east, west, up, down
        """
        block_types = {
            "impulse": "minecraft:command_block",
            "repeating": "minecraft:repeating_command_block",
            "chain": "minecraft:chain_command_block"
        }
        bt = block_types.get(mode.lower(), "minecraft:command_block")
        
        # Build block state
        state = f"[facing={facing},conditional={str(conditional).lower()}]"
        
        # Build NBT
        # auto=1 makes it "Always Active", auto=0 is "Needs Redstone"
        nbt = f'{{Command:"{command_to_run}",auto:{1 if auto else 0}b}}'
        
        # Use setblock with state and NBT
        full_command = f'setblock {x} {y} {z} {bt}{state}{nbt}'
        return self.send_command(full_command)

