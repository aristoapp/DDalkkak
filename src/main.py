from __future__ import annotations

import asyncio
import logging

from src.agent.appium_agent import AppiumAgent
from src.cli.app import CLIApp
from src.intent.parser import IntentParser
from src.router.router import ServiceRouter
from src.services.delivery import BaeminHandler, CoupangEatsHandler
from src.services.gift import KakaoGiftHandler
from src.services.mobility import KakaoTHandler
from src.services.reservation import CatchtableHandler, NaverReservationHandler
from src.services.shopping import CoupangHandler, NaverShoppingHandler
from src.services.travel import YanoljaHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ddalkkak")


async def run() -> None:
    agent = AppiumAgent()
    parser = IntentParser()
    router = ServiceRouter()

    logger.info("Initializing Appium agent...")
    ok = await agent.initialize()
    if not ok:
        logger.error("Appium agent initialization failed!")
        raise RuntimeError("Failed to initialize Appium agent")
    logger.info("Appium agent initialized")

    handlers = {
        "coupang": CoupangHandler(agent),
        "naver_shopping": NaverShoppingHandler(agent),
        "baemin": BaeminHandler(agent),
        "coupang_eats": CoupangEatsHandler(agent),
        "kakaot": KakaoTHandler(agent),
        "yanolja": YanoljaHandler(agent),
        "catchtable": CatchtableHandler(agent),
        "naver_reservation": NaverReservationHandler(agent),
        "kakao_gift": KakaoGiftHandler(agent),
    }
    logger.info("Registered %d service handlers", len(handlers))

    app = CLIApp(parser=parser, router=router, agent=agent, handlers=handlers)
    try:
        await app.run()
    finally:
        await agent.cleanup()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
