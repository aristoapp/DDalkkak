from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    anthropic_api_key: str

    # Android package names (Play Store / adb package names)
    coupang_package: str = "com.coupang.mobile"
    baemin_package: str = "com.baemin"
    coupang_eats_package: str = "com.coupang.coupangeats"
    kakaot_package: str = "com.kakao.taxi"
    naver_package: str = "com.nhn.android.search"
    yanolja_package: str = "com.yanolja.local"
    catchtable_package: str = "co.catchtable.catchtable"
    kakao_package: str = "com.kakao.talk"

    # Droidrun / device
    device_serial: str = "emulator-5554"
    max_steps: int = 30
    vision_enabled: bool = True
    reasoning_enabled: bool = False
    save_trajectory: str = "step"
    trajectory_path: str = "trajectories"
    device_use_tcp: bool = False
    droidrun_anthropic_model: str = "claude-sonnet-4-20250514"


settings = Settings()
