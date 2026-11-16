//! 로컬 실행용 서버. 127.0.0.1에만 바인딩한다.

use std::net::SocketAddr;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let router = fde_study::router()?;
    let port: u16 = match std::env::var("FDE_PORT") {
        Ok(v) => v
            .parse()
            .map_err(|_| format!("FDE_PORT 값이 포트 번호가 아닙니다: {v}"))?,
        Err(_) => 8787,
    };
    // localhost 전용. 외부 공개가 필요하면 바인딩 주소를 명시적으로 바꿔야 한다.
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let listener = tokio::net::TcpListener::bind(addr).await?;
    println!("FDE 학습 공간: http://{addr}");
    axum::serve(listener, router).await?;
    Ok(())
}
