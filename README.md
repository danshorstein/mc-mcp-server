# Minecraft OverWatch MCP Server

An MCP (Model Context Protocol) server that gives AI agents "God-mode" control over Minecraft via the [GDMC HTTP mod](https://github.com/Niels-NTG/gdmc_http_interface).

## Features
- **Spatial Awareness**: The AI knows where you are and what you're looking at.
- **World Management**: Inspect blocks, get build area bounds, and monitor world state.
- **Mass Block Editing**: Uses optimized `fill` batching for near-instant construction.
- **Data Visualization**: Render images directly into the Minecraft world with high-quality dithering.
- **Smart Rendering**: Only updates blocks that have changed (using differential state tracking).

## Installation & Usage

### Option 1: Zero-Install (Run from GitHub)
The easiest way to run this server is via `uvx` (part of the [uv](https://astral.sh/uv/) ecosystem). This runs the server directly from GitHub without manual cloning or setup.

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/YOUR_USERNAME/mc-mcp-server",
        "mc-mcp"
      ],
      "env": {
        "GDMC_URL": "http://localhost:9000"
      }
    }
  }
}
```

### Option 2: Local Development Setup
1. **Clone & Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install .
   ```

2. **Run**:
   ```bash
   mc-mcp
   ```

## Configuration for Claude Desktop (Local)

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "minecraft": {
      "command": "/ABSOLUTE/PATH/TO/mc-mcp-server/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/mc-mcp-server/server.py"],
      "env": {
        "GDMC_URL": "http://localhost:9000"
      }
    }
  }
}
```

## Tools Included

- `get_player_context`: Returns coordinates, rotation, and cardinal facing.
- `get_build_area`: Returns the currently defined build area bounds.
- `get_blocks_in_region`: Inspect block data in a specific area.
- `get_world_state`: Monitor time, weather, and world info.
- `run_minecraft_command`: **God-mode**: Execute ANY raw Minecraft command.
- `spawn_entities`: **God-mode**: Mass-spawn mobs or entities.
- `control_world`: **God-mode**: Manipulate weather, time, and gamerules.
- `place_command_block`: **Automation**: Precise placement of impulse/repeating command blocks with scripts.
- `place_block` / `fill_area`: Precise or mass block placement.
- `render_image_to_screen`: Optimized image-to-block rendering.
- `clear_screen`: Wipes rendered screens at a specific location.



## Development

Run unit tests:
```bash
python -m unittest tests/test_utils.py
```

## License
MIT License - see [LICENSE](LICENSE) for details.
