# eyeshot-mcp

> Built by DeepSeek

[中文](README_zh.md)

**No telemetry, no external calls, no data exfiltration.** Screenshots never leave your machine unless you explicitly send them to the vision API endpoint you configured.

Eyeshot (Screenshot + Vision) — two MCP tools that give your AI the ability to **see**, forming an automated **capture → analyze** pipeline on Windows.

**If your AI already has vision (GPT-4V, Claude, etc.), you only need the screenshot MCP.** The vision MCP is for AIs without built-in vision support.

## Compatibility

Works with any MCP-compatible client: **opencode**, **Claude Desktop**, **Cursor**, **VS Code** (via extensions), or any other MCP host. These are standard MCP tools — not tied to any specific platform.

## Use Cases

- Automated UI testing — After writing frontend code, let AI launch the browser, screenshot, and verify the page
- OCR text recognition — Capture a window or full screen, read text via vision model
- App UI verification — Launch a desktop app, screenshot, and check if UI renders correctly
- AI-assisted debugging — Program crashes? Take a screenshot and let AI look at it

## Installation

### Option 1: Let AI install it (Recommended)

Send this prompt to your AI assistant, it will handle everything:

> "Clone https://github.com/yourname/eyeshot-mcp to my machine, install its dependencies, then configure it as an MCP server in my opencode config file."

### Option 2: Manual install

```bash
git clone https://github.com/yourname/eyeshot-mcp.git
pip install -r requirements.txt
```

## Configuration

### opencode

Add to `~\.config\opencode\opencode.jsonc`:

```jsonc
{
  "mcp": {
    "screenshot": {
      "type": "local",
      "command": ["python", "C:\\path\\to\\eyeshot-mcp\\screenshot_mcp.py"],
      "enabled": true
    },
    "vision": {
      "type": "local",
      "command": ["python", "C:\\path\\to\\eyeshot-mcp\\vision_mcp.py"],
      "enabled": true
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VISION_API_KEY` | (required) | Vision API key |
| `VISION_API_URL` | `https://api.openai.com/v1/chat/completions` | API endpoint. Also works with [OpenRouter](https://openrouter.ai) (`https://openrouter.ai/api/v1/chat/completions`) |
| `VISION_MODEL` | `gpt-4o` | Vision model name. Any VL model works, e.g. `qwen/qwen2.5-vl-32b-instruct` via OpenRouter |
| `VISION_MAX_WIDTH` | `2048` | Max image width sent to API (0 = no resize) |
| `VISION_MAX_TOKENS` | `512` | Max tokens in API response |
| `SCREENSHOT_BROWSER_CLASSES` | (optional) | Comma-separated extra browser window classes |

## Tool Reference

### `screenshot_capture_to_file`

Capture an existing window or full screen, save to `screenshot.png`, return path.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `window_title` | str | `""` | Window title, empty = full screen |
| `resize_width` | int | `0` | Screenshot resize width, 0 = auto based on display resolution |

**Auto-resolution logic:**
- 4K (3840) → resize to 1920
- 1440p (2560) → resize to 1280
- 1080p (1920) → resize to 960
- Below 1920 → no resize, keep original

### `screenshot_test_window`

Launch program → Wait → Capture → Close (fully automatic).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | str | required | Launch command, browsers must include `--new-window` |
| `wait_seconds` | int | required | Wait seconds after launch |
| `maximized` | bool | required | Whether to maximize the window |
| `window_title` | str | `""` | Which window to capture; empty = full screen, no close |
| `resize_width` | int | `0` | Same as capture_to_file |

**Browser tab protection:** When a browser is detected without `--new-window`, closing is skipped to protect other tabs. With `--new-window`, the exclusive window is closed normally.

### `vision_analyze_image`

Analyze an image with a vision model, return text result.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | str | required | Image path, e.g. `screenshot.png` |
| `prompt` | str | `"描述这张图片的内容"` | Your question, supports any language |

## Browser Support

| Window Class | Browser |
|-------------|---------|
| `Chrome_WidgetWin_1` | Chrome, Edge (Chromium), Brave, Opera, Vivaldi |
| `MozillaWindowClass` | Firefox |
| `MSEdgeWindowClass` | Edge (UWP / legacy) |
| `ApplicationFrameWindow` | UWP apps & WebView |

Add custom classes: `SCREENSHOT_BROWSER_CLASSES=MyClass1,MyClass2`

## FAQ

**Q: Screenshot text is blurry?**
A: Increase `resize_width` (e.g. `4096`) to keep original resolution.

**Q: Don't know the window title?**
A: Use `tasklist` to list running processes, or capture full screen and let the vision model identify it.

**Q: Why didn't the browser window close?**
A: Closing is skipped without `--new-window` to protect other tabs. Add `--new-window` to your launch command.

**Q: Can I use a different vision model?**
A: Yes. Set `VISION_API_URL` and `VISION_MODEL` env vars. Compatible with any OpenAI-compatible API.

MIT
