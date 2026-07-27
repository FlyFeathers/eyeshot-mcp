import base64
import io
import os
import json
import urllib.request
from PIL import Image
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vision")

KEY = os.environ.get("VISION_API_KEY")
URL = os.environ.get("VISION_API_URL", "https://api.openai.com/v1/chat/completions")
MODEL = os.environ.get("VISION_MODEL", "gpt-4o")
MAX_WIDTH = int(os.environ.get("VISION_MAX_WIDTH", 2048))
MAX_TOKENS = int(os.environ.get("VISION_MAX_TOKENS", 512))


@mcp.tool()
def analyze_image(file_path: str, prompt: str = "描述这张图片的内容") -> str:
    """Analyze an image with a vision model / 用视觉模型分析图片。

    file_path: path to screenshot (e.g. screenshot.png).
    prompt: optional question in any language.

    Use after screenshot_capture_to_file or screenshot_test_window:
    capture → analyze → return result.

    API key via VISION_API_KEY env var.
    """
    img = Image.open(file_path).convert("RGB")
    if MAX_WIDTH > 0 and img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    b64 = base64.b64encode(buf.getvalue()).decode()

    body = json.dumps({
        "model": MODEL, "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]}]
    }).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {KEY}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


if __name__ == "__main__":
    mcp.run()
