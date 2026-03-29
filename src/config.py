from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    anthropic_api_key: str
    minitap_api_key: str = ""

    coupang_bundle_id: str = "com.coupang.Coupang"
    baemin_bundle_id: str = "com.woowahan.deliveryapp"
    coupang_eats_bundle_id: str = "com.coupang.CoupangEats"
    kakaot_bundle_id: str = "com.kakao.taxi"
    naver_bundle_id: str = "com.nhn.NaverSearch"
    yanolja_bundle_id: str = "com.yanolja.yanoljaapp"
    catchtable_bundle_id: str = "com.catchtable.catchtable"
    kakao_bundle_id: str = "com.kakao.talk"

    minitap_max_steps: int = 400
    minitap_task_interval_seconds: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
