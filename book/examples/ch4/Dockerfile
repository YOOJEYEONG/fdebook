# 4.4 컨테이너 이미지: 4.1의 API를 담는 예시. 빌드: docker build -t tickets-api -f examples/ch4/Dockerfile examples/ch4
# 버전을 고정해 같은 Dockerfile이 언제 빌드해도 같은 기반에서 시작하게 한다.
FROM python:3.13-slim

# 루트가 아닌 사용자로 실행한다: 컨테이너가 뚫려도 피해 범위가 줄어든다.
RUN useradd --create-home --uid 10001 app
WORKDIR /app

# 바뀌지 않는 파일을 먼저 복사하면 빌드 캐시를 재사용한다(이 예제는 의존성이 없어 바로 코드).
COPY tickets_api.py serve.py ./

USER app
EXPOSE 8080
# 비밀값은 이미지에 넣지 않는다. 실행할 때 환경 변수나 비밀 저장소로 넘긴다(4.3절).
CMD ["python", "serve.py"]
