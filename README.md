# Minecraft OverWatch MCP Server

An MCP (Model Context Protocol) server that gives AI agents "God-mode" control over Minecraft via the [GDMC HTTP mod](https://github.com/Niels-NTG/gdmc_http_interface).

## Features
- **Spatial Awareness**: The AI knows where you are and what you're looking at.
- **Mass Block Editing**: Uses optimized `fill` batching for near-instant construction.
- **Data Visualization**: Render images, charts, and dashboards directly into the Minecraft world with high-quality dithering.

## Installation

1. **Install GDMC HTTP Mod**:
   - Ensure you have the GDMC HTTP interface mod installed and running in your Minecraft instance (default port 9000).

2. **Setup Dependencies**:
   ```bash
   pip install mcp requests pillow numpy
   ```

3. **Run the Server**:
   ```bash
   python server.py
   ```

## Configuration for Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "minecraft": {
      "command": "python3",
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
- `place_block`: Simple single-block placement.
- `fill_area`: Standard mass fill command for boxes.
- `render_image_to_screen`: Optimized image-to-block rendering.
- `clear_screen`: Wipes rendered screens at a specific location.

## GitHub Push Instructions

1. Create a new repository on GitHub named `mc-mcp-server`.
2. run the following in this directory:
   ```bash
   git init
   git add .
   git commit -m "initial commit: Minecraft OverWatch MCP Server"
   git remote add origin https://github.com/YOUR_USERNAME/mc-mcp-server.git
   git push -u origin main
   ```
