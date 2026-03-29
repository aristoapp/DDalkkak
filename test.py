"""Quick Droidrun Portal + ADB connectivity check. Run: uv run python test.py"""

from __future__ import annotations

import asyncio

from droidrun.tools import AndroidDriver

from src.config import settings


async def main() -> None:
    driver = AndroidDriver(serial=settings.device_serial, use_tcp=settings.device_use_tcp)
    await driver.connect()
    print(f"Connected to device: {settings.device_serial}")
    png = await driver.screenshot()
    out = "test_screenshot.png"
    with open(out, "wb") as f:
        f.write(png)
    print(f"Screenshot saved to {out}")


if __name__ == "__main__":
    asyncio.run(main())
