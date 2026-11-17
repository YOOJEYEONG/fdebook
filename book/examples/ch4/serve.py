"""컨테이너 진입점: 4.1의 API를 0.0.0.0:8080에서 띄운다(컨테이너 밖에서 접속하려면 모든 인터페이스에 바인딩)."""
import os
from http.server import ThreadingHTTPServer

from tickets_api import make_server, open_db

server = make_server(open_db())
handler = server.RequestHandlerClass
server.server_close()
port = int(os.environ.get("PORT", "8080"))
print(f"listening on 0.0.0.0:{port}", flush=True)
ThreadingHTTPServer(("0.0.0.0", port), handler).serve_forever()
