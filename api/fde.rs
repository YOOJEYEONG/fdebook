//! Vercel 함수 진입점. vercel/examples의 rust/axum 공식 패턴(VercelLayer + vercel_runtime::run)을 따른다.
//! 라우터와 렌더링은 로컬 서버와 같은 fde_study::router()를 재사용한다.

use tower::ServiceBuilder;
use vercel_runtime::{Error, axum::VercelLayer};

#[tokio::main]
async fn main() -> Result<(), Error> {
    let router = fde_study::router()?;
    let app = ServiceBuilder::new()
        .layer(VercelLayer::new())
        .service(router);
    vercel_runtime::run(app).await
}
