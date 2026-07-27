import os
import time
import subprocess
import ctypes
from ctypes import wintypes
import mss
from PIL import Image
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("screenshot")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32
user32.SetProcessDPIAware()

SW_RESTORE = 9
WM_CLOSE = 0x0010
HORZRES = 8

_BROWSER_CLASSES = {"Chrome_WidgetWin_1", "MozillaWindowClass", "MSEdgeWindowClass", "ApplicationFrameWindow"}
_env_extras = os.environ.get("SCREENSHOT_BROWSER_CLASSES", "")
if _env_extras:
    _BROWSER_CLASSES.update(s.strip() for s in _env_extras.split(",") if s.strip())


def _get_display_width():
    dc = user32.GetDC(0)
    w = gdi32.GetDeviceCaps(dc, HORZRES)
    user32.ReleaseDC(0, dc)
    return w


def _default_resize_width():
    display_w = _get_display_width()
    return min(int(display_w * 0.5), 1920)


def _get_window_class(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _get_window_text(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value


def _activate_window(hwnd):
    prev = user32.GetForegroundWindow()
    if prev == hwnd:
        return prev
    prev_tid = user32.GetWindowThreadProcessId(prev, 0)
    cur_tid = kernel32.GetCurrentThreadId()
    attached = prev_tid != cur_tid
    if attached:
        user32.AttachThreadInput(cur_tid, prev_tid, True)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    if attached:
        user32.AttachThreadInput(cur_tid, prev_tid, False)
    return prev


def _restore_foreground(hwnd):
    if not hwnd:
        return
    prev_tid = user32.GetWindowThreadProcessId(hwnd, 0)
    cur_tid = kernel32.GetCurrentThreadId()
    attached = prev_tid != cur_tid
    if attached:
        user32.AttachThreadInput(cur_tid, prev_tid, True)
    user32.SetForegroundWindow(hwnd)
    if attached:
        user32.AttachThreadInput(cur_tid, prev_tid, False)


def _score_title(query_lower, title):
    title_lower = title.lower()

    if query_lower == title_lower:
        return 100

    core = title_lower.split(" - ")[0].strip()
    if query_lower == core:
        return 100

    if title_lower.startswith(query_lower):
        return 90

    if " - " in title_lower:
        suffix = title_lower.split(" - ", 1)[1].strip()
        if suffix.startswith(query_lower) or query_lower == suffix:
            return 85
        if query_lower in suffix:
            return 70

    qwords = query_lower.split()
    twords = title_lower.split()
    if all(any(w == tw for tw in twords) for w in qwords):
        return 80

    if query_lower in title_lower:
        return 50

    return 0


def _find_window(title):
    candidates = []
    query_lower = title.lower()

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        wtitle = _get_window_text(hwnd)
        if not wtitle:
            return True
        score = _score_title(query_lower, wtitle)
        if score > 0:
            r = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            candidates.append((score, hwnd, wtitle, r))
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)

    if not candidates:
        return None, f"未找到标题包含 '{title}' 的窗口"

    candidates.sort(key=lambda x: -x[0])
    best_score = candidates[0][0]
    top = [c for c in candidates if c[0] == best_score]

    if len(top) > 1:
        names = "\n".join(f"  - {c[2]}" for c in top)
        return None, (
            f"多个窗口匹配 '{title}'，请使用更精确的标题:\n{names}"
        )

    hwnd = top[0][1]
    r = top[0][3]
    return (hwnd, (r.left, r.top, r.right - r.left, r.bottom - r.top)), None


def _get_cwd():
    for arg in __import__("sys").argv:
        if arg.startswith("--cwd="):
            return arg[6:]
    return os.getcwd()


def _capture(window_title, resize_width):
    if resize_width <= 0:
        resize_width = _default_resize_width()
    hwnd = None
    with mss.mss() as sct:
        if window_title:
            found, err = _find_window(window_title)
            if err:
                return None, err, None
            hwnd, rect = found
            prev = _activate_window(hwnd)
            time.sleep(0.3)

            monitor = {"left": rect[0], "top": rect[1],
                       "width": rect[2], "height": rect[3]}
            screenshot = sct.grab(monitor)

            if prev:
                _restore_foreground(prev)
        else:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX").convert("RGB")
        if img.width > resize_width:
            ratio = resize_width / img.width
            img = img.resize((resize_width, int(img.height * ratio)), Image.LANCZOS)
        return img, None, hwnd


@mcp.tool()
def capture_to_file(window_title: str = "", resize_width: int = 0) -> str:
    """Capture a window or full screen to screenshot.png / 截图保存到screenshot.png。

    Use for existing windows; for launching programs use test_window instead.
    Specify window_title for targeted capture (faster); omit for full screen.
    Brings target window to front before capture, restores previous window after.

    resize_width: 0 = auto (half display width, max 1920). Pass large value
    (e.g. 4096) to keep original resolution for OCR.

    Pair with vision_analyze_image to complete the automation chain.
    """
    img, err, _ = _capture(window_title, resize_width)
    if err:
        return err
    path = os.path.join(_get_cwd(), "screenshot.png")
    img.save(path, format="PNG")
    return path


@mcp.tool()
def test_window(command: str, wait_seconds: int, maximized: bool, window_title: str = "", resize_width: int = 0) -> str:
    """[Auto-test] Launch program → wait → capture → close / 启动→等→截→关。

    Full automation chain: "write code → run → see UI → close". Also for manual testing.

    command: launch command (e.g. notepad.exe). Browsers must include --new-window.
    wait_seconds: seconds to wait after launch (required; 1s for local, more for web).
    maximized: maximize the window (required; recommended for browsers).
    window_title: which window to capture (strongly recommended; empty = full screen, no close).

    Returns screenshot path or error message.
    """
    si = subprocess.STARTUPINFO()
    si.dwFlags = 1
    si.wShowWindow = 3 if maximized else 1
    proc = subprocess.Popen(command, shell=True, startupinfo=si)
    time.sleep(wait_seconds)

    if maximized and window_title:
        found, _ = _find_window(window_title)
        if found:
            user32.ShowWindow(found[0], 3)

    img, err, hwnd = _capture(window_title, resize_width)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if hwnd:
        is_browser = _get_window_class(hwnd) in _BROWSER_CLASSES
        has_new_window = "--new-window" in command
        if is_browser and not has_new_window:
            pass
        else:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

    if err:
        return err
    path = os.path.join(_get_cwd(), "screenshot.png")
    img.save(path, format="PNG")
    return path


if __name__ == "__main__":
    mcp.run()
