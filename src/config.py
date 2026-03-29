from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str

    coupang_bundle_id: str = "com.coupang.Coupang"
    baemin_bundle_id: str = "com.jawebs.baedal"
    coupang_eats_bundle_id: str = "com.coupang.coupang-eats"
    kakaot_bundle_id: str = "com.kakao.taxi"
    naver_bundle_id: str = "com.nhncorp.NaverSearch"
    yanolja_bundle_id: str = "com.yanolja.motel"
    catchtable_bundle_id: str = "co.catchtable.m"
    kakao_bundle_id: str = "com.iwilab.KakaoTalk"

    device_udid: str = "00008120-00064DE22ED1A01E"
    appium_host: str = "http://127.0.0.1:4723"
    appium_max_steps: int = 30
    appium_step_interval: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
