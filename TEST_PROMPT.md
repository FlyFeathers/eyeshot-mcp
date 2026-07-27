Run the following tests in order. Report PASS/FAIL after each one.

---

## Test 1: Resolution-adaptive screenshot

Use `screenshot_capture_to_file` with `resize_width=0` (auto mode):
- Confirm `screenshot.png` was created in the current working directory
- Use `vision_analyze_image` on it, asking "What are the pixel dimensions of this image?"
- Verify: width should be auto-calculated, not hardcoded to 1440

---

## Test 2: Window title capture

1. Open Notepad, type "Hello eyeshot test 123", window title is "Untitled - Notepad"
2. Use `screenshot_capture_to_file` with `window_title="Untitled - Notepad"`
3. Use `vision_analyze_image` on the screenshot, asking "What text is visible in this image?"
- Verify: vision result includes "Hello eyeshot test 123"

---

## Test 3: test_window automation (desktop app)

Use `screenshot_test_window`:
- `command="notepad.exe"`
- `wait_seconds=1`
- `maximized=false`
- `window_title="Untitled - Notepad"`
- `resize_width=0`
Verify: screenshot saved + Notepad window is closed.

---

## Test 4: test_window automation (browser + --new-window)

Use `screenshot_test_window`:
- `command="start msedge --new-window https://example.com"`
- `wait_seconds=2`
- `maximized=true`
- `window_title="Example Domain"`
- `resize_width=0`
Verify: screenshot saved + Edge window is closed.

---

## Test 5: Browser tab protection (no --new-window)

Use `screenshot_test_window`:
- `command="start msedge https://example.com"`
- `wait_seconds=2`
- `maximized=true`
- `window_title="Example Domain"`
- `resize_width=0`
Verify: screenshot saved + Edge window is NOT closed.

---

## Test 6: Non-existent window title

Use `screenshot_capture_to_file` with `window_title="XYZNonExistentWindow12345"`:
- Verify: returns a clear error message, no crash
- Then use `tasklist` to list running processes and explain how to find the correct window title

---

## Test 7: Full-screen vision analysis

Use `screenshot_capture_to_file` (no window_title, resize_width=4096), then `vision_analyze_image` asking "Describe the visible text content in this screenshot":
- Verify: a meaningful text description is returned

---

## Summary

Output a table:

| Test | Result | Notes |
|------|--------|-------|
| 1 Auto resolution | | |
| 2 Window title capture | | |
| 3 test_window desktop | | |
| 4 Browser + --new-window | | |
| 5 Tab protection | | |
| 6 Non-existent window | | |
| 7 Full-screen vision | | |
