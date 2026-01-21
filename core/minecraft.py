import requests
import re
import math
import json

class MinecraftInterface:
    def __init__(self, base_url='http://localhost:9000'):
        self.base_url = base_url

    def send_command(self, command):
        """Send a command to Minecraft via GDMC HTTP."""
        try:
            url = f'{self.base_url}/command'
            response = requests.post(url, data=command, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Command error: {e}")
            return False

    def get_player_info(self):
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
        except Exception as e:
            print(f"Could not get player info: {e}")
        return None

    def fill_region(self, x1, y1, z1, x2, y2, z2, block_type):
        """Execute a /fill command."""
        if not block_type.startswith("minecraft:"):
            block_type = f"minecraft:{block_type}"
        command = f'fill {int(x1)} {int(y1)} {int(z1)} {int(x2)} {int(y2)} {int(z2)} {block_type}'
        return self.send_command(command)

    def set_block(self, x, y, z, block_type):
        """Execute a /setblock command."""
        if not block_type.startswith("minecraft:"):
            block_type = f"minecraft:{block_type}"
        command = f'setblock {int(x)} {int(y)} {int(z)} {block_type}'
        return self.send_command(command)

    def tellraw(self, message, color="white"):
        """Send a tellraw message to all players."""
        payload = json.dumps([
            "",
            {"text": "🤖 [MCP] ", "color": "aqua", "bold": True},
            {"text": message, "color": color}
        ])
        return self.send_command(f'tellraw @a {payload}')
