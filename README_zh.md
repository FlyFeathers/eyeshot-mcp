# eyeshot-mcp

> 由 DeepSeek 构建

[English](README.md)

**无遥测、无外联、无数据泄漏。** 截图绝不离开你的机器，除非你显式调用视觉 API 发送到你配置的端点。

Eyeshot（截图 + 识图）给 AI 用的 Windows 自动化视觉链路，两个 MCP 工具组成**截图→识图**闭环。

**如果你的 AI 已有视觉能力（GPT-4V、Claude 等），只需装截图 MCP。** 识图 MCP 是给没有内置视觉的 AI 用的。

## 兼容性

适用于任何 MCP 兼容客户端：**opencode**、**Claude Desktop**、**Cursor**、**VS Code**（通过扩展）等。这是标准 MCP 工具，不绑定任何特定平台。

## 使用场景

- 自动化 UI 测试 — 写完前端代码，让 AI 自己启动浏览器、截图、识别页面是否正确
- OCR 文字识别 — 截取窗口/全屏，视觉模型读取上面的文字
- 应用界面验证 — 启动桌面应用，截图分析界面元素是否渲染正常
- AI 辅助调试 — 程序报错了，截个图给 AI 看，不用你描述

## 安装

### 方式一：让 AI 帮你装（推荐）

把这句话发给你的 AI 助手，它会自动完成全部配置：

> "Clone https://github.com/yourname/eyeshot-mcp to my machine, install its dependencies, then configure it as an MCP server in my opencode config file."

### 方式二：手动安装

```bash
git clone https://github.com/yourname/eyeshot-mcp.git
pip install -r requirements.txt
```

## 配置

### opencode

在 `~\.config\opencode\opencode.jsonc` 中添加：

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

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VISION_API_KEY` | （必填） | 视觉模型 API Key |
| `VISION_API_URL` | `https://api.openai.com/v1/chat/completions` | API 端点（OpenAI 兼容协议） |
| `VISION_MODEL` | `gpt-4o` | 视觉模型名 |
| `VISION_MAX_WIDTH` | `2048` | 发送给 API 的图片最大宽度（0=不缩放） |
| `VISION_MAX_TOKENS` | `512` | API 返回的最大 token 数 |
| `SCREENSHOT_BROWSER_CLASSES` | （可选） | 追加浏览器窗口类名，逗号分隔 |

## 工具说明

### `screenshot_capture_to_file`

截取已存在的窗口或全屏，保存为 `screenshot.png` 并返回路径。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `window_title` | str | `""` | 窗口标题，空串=全屏 |
| `resize_width` | int | `0` | 截图缩放宽度，0=根据屏幕分辨率自动计算 |

**自适应分辨率逻辑：**
- 4K (3840) → 缩至 1920
- 1440p (2560) → 缩至 1280
- 1080p (1920) → 缩至 960
- 低于 1920 → 不缩放，保持原分辨率

### `screenshot_test_window`

启动程序 → 等待 → 截图 → 关闭（全自动）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `command` | str | 必填 | 启动命令，浏览器务必加 `--new-window` |
| `wait_seconds` | int | 必填 | 启动后等待秒数 |
| `maximized` | bool | 必填 | 是否最大化窗口 |
| `window_title` | str | `""` | 截哪窗口；空=截全屏且不关窗口 |
| `resize_width` | int | `0` | 同 capture_to_file |

**浏览器标签保护：** 检测到浏览器窗口且命令中无 `--new-window` 时，跳过关闭以保护其他标签页。有 `--new-window` 则正常关闭独占窗口。

### `vision_analyze_image`

用视觉模型分析图片，返回文字结果。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file_path` | str | 必填 | 图片路径，如 `screenshot.png` |
| `prompt` | str | `"描述这张图片的内容"` | 你想问的问题，支持中文 |

## 浏览器支持

| 窗口类 | 浏览器 |
|--------|--------|
| `Chrome_WidgetWin_1` | Chrome、Edge (Chromium)、Brave、Opera、Vivaldi |
| `MozillaWindowClass` | Firefox |
| `MSEdgeWindowClass` | Edge (UWP / 旧版) |
| `ApplicationFrameWindow` | UWP 应用 & WebView |

如需追加自定义窗口类：`SCREENSHOT_BROWSER_CLASSES=MyClass1,MyClass2`

## 常见问题

**Q: 截图文字看不清？**
A: 增大 `resize_width`（如 `4096`）保留原分辨率。

**Q: 不知道窗口标题叫什么？**
A: 用 `tasklist` 查进程，或先截全屏再让视觉模型识别。

**Q: 为什么浏览器窗口没关？**
A: 无 `--new-window` 时跳过关闭以保护其他标签页。请给启动命令加 `--new-window`。

**Q: 能用其他视觉模型吗？**
A: 可以。设 `VISION_API_URL` 和 `VISION_MODEL` 环境变量即可，兼容任何 OpenAI 兼容 API。

MIT
