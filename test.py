import asyncio
from minitap.mobile_use.sdk import Agent


async def test():
    agent = Agent()
    ok = await agent.init()
    print(f"Agent initialized: {ok}")
    screenshot = await agent.get_screenshot()
    screenshot.save("test_screenshot.png")
    print("Screenshot saved to test_screenshot.png")
    await agent.clean()
    print("Agent cleaned up")


asyncio.run(test())
