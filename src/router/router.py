from src.config import settings
from src.intent.schemas import ParsedIntent, ServiceCategory

# Category → (app_key, bundle_id, display_name)
SERVICE_MAP = {
    ServiceCategory.SHOPPING: [
        ("coupang", settings.coupang_bundle_id, "쿠팡"),
        ("naver_shopping", settings.naver_bundle_id, "네이버쇼핑"),
    ],
    ServiceCategory.DELIVERY: [
        ("baemin", settings.baemin_bundle_id, "배달의민족"),
        ("coupang_eats", settings.coupang_eats_bundle_id, "쿠팡이츠"),
    ],
    ServiceCategory.MOBILITY: [
        ("kakaot", settings.kakaot_bundle_id, "카카오T"),
    ],
    ServiceCategory.TRAVEL: [
        ("yanolja", settings.yanolja_bundle_id, "야놀자"),
    ],
    ServiceCategory.RESERVATION: [
        ("catchtable", settings.catchtable_bundle_id, "캐치테이블"),
        ("naver_reservation", settings.naver_bundle_id, "네이버예약"),
    ],
    ServiceCategory.GIFT: [
        ("kakao_gift", settings.kakao_bundle_id, "카카오톡 선물하기"),
    ],
}


class ServiceRouter:
    def route(self, intent: ParsedIntent) -> tuple[str, str, str]:
        """Resolve to (app_key, bundle_id, display_name) given an intent."""
        services = SERVICE_MAP.get(intent.category, [])
        if not services:
            raise ValueError(f"No service mapping for {intent.category}")

        # If user specified a preferred app, honor it
        if intent.app_preference:
            for app_key, bundle_id, name in services:
                if app_key == intent.app_preference:
                    intent.app_target = app_key
                    return (app_key, bundle_id, name)

        # Default to the first service in the category
        app_key, bundle_id, name = services[0]
        intent.app_target = app_key
        return (app_key, bundle_id, name)
