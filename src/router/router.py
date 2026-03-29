from src.config import settings
from src.intent.schemas import ParsedIntent, ServiceCategory

# Category → (app_key, package_name, display_name)
SERVICE_MAP = {
    ServiceCategory.SHOPPING: [
        ("coupang", settings.coupang_package, "쿠팡"),
        ("naver_shopping", settings.naver_package, "네이버쇼핑"),
    ],
    ServiceCategory.DELIVERY: [
        ("baemin", settings.baemin_package, "배달의민족"),
        ("coupang_eats", settings.coupang_eats_package, "쿠팡이츠"),
    ],
    ServiceCategory.MOBILITY: [
        ("kakaot", settings.kakaot_package, "카카오T"),
    ],
    ServiceCategory.TRAVEL: [
        ("yanolja", settings.yanolja_package, "야놀자"),
    ],
    ServiceCategory.RESERVATION: [
        ("catchtable", settings.catchtable_package, "캐치테이블"),
        ("naver_reservation", settings.naver_package, "네이버예약"),
    ],
    ServiceCategory.GIFT: [
        ("kakao_gift", settings.kakao_package, "카카오톡 선물하기"),
    ],
}


class ServiceRouter:
    def route(self, intent: ParsedIntent) -> tuple[str, str, str]:
        """Resolve to (app_key, package_name, display_name) given an intent."""
        services = SERVICE_MAP.get(intent.category, [])
        if not services:
            raise ValueError(f"No service mapping for {intent.category}")

        # If user specified a preferred app, honor it
        if intent.app_preference:
            for app_key, package_name, name in services:
                if app_key == intent.app_preference:
                    intent.app_target = app_key
                    return (app_key, package_name, name)

        # Default to the first service in the category
        app_key, package_name, name = services[0]
        intent.app_target = app_key
        return (app_key, package_name, name)
