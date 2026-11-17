"""4.3 설정과 비밀값: 환경 변수에서 읽고, 시작할 때 검증하고, 비밀값은 출력하지 않는다."""
import os
from dataclasses import dataclass, field


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Secret:
    """값을 들고 있지만 print나 로그에 찍혀도 내용을 드러내지 않는다."""
    value: str = field(repr=False)

    def __str__(self):
        return "***"

    def __repr__(self):
        return "Secret(***)"


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    request_timeout_s: float
    api_token: Secret


def load(env):
    missing = [k for k in ("APP_ENV", "DATABASE_URL", "API_TOKEN") if not env.get(k)]
    if missing:
        raise ConfigError(f"필수 설정 없음: {', '.join(missing)}")
    if env["APP_ENV"] not in ("dev", "staging", "prod"):
        raise ConfigError(f"APP_ENV는 dev/staging/prod 중 하나여야 합니다: {env['APP_ENV']!r}")
    try:
        timeout = float(env.get("REQUEST_TIMEOUT_S", "5"))
    except ValueError:
        raise ConfigError("REQUEST_TIMEOUT_S는 숫자여야 합니다") from None
    return Settings(env["APP_ENV"], env["DATABASE_URL"], timeout, Secret(env["API_TOKEN"]))


# 1) 실제 프로세스 환경에서 읽는다(실행 명령에서 넘긴 값).
settings = load(os.environ)
print("설정:", settings)
print("토큰 길이만 확인:", len(settings.api_token.value))

# 2) 잘못된 설정은 시작 단계에서 막는다. 운영 중에 처음 터지는 것보다 낫다.
for bad in ({"APP_ENV": "prod"}, {"APP_ENV": "production", "DATABASE_URL": "x", "API_TOKEN": "t"},
            {"APP_ENV": "dev", "DATABASE_URL": "x", "API_TOKEN": "t", "REQUEST_TIMEOUT_S": "5초"}):
    try:
        load(bad)
    except ConfigError as error:
        print("시작 거부:", error)
