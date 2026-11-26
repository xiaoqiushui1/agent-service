from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
import uvicorn

from app.modules.chat_thread.exceptions import ChatThreadNotFoundError

# 初始化日志系统
configure_logging(settings.logging.level)
logger = get_logger(__name__)#获得模块的名字



# 生命周期管理（预留）
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.database import check_database, close_database
    try:
        await check_database()
        yield
    finally:
        logger.info("应用关闭中... ")
        await close_database()

app = FastAPI(#初始化fastapi生命周期的配置
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan
)
from app.modules.product.router import router as product_router

# 创建 app 后注册路由
app.include_router(product_router)
#ai创建会话
from app.modules.chat_thread.router import router as chat_thread_router
app.include_router(chat_thread_router)

@app.get("/health", summary="健康检测接口")
async def health_check() -> dict[str, str]:
    logger.info("执行健康检查")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )
# 统一处理异常信息，发现是ChatThreadNotFoundError，返回对应的错误状态码和错误信息
@app.exception_handler(ChatThreadNotFoundError) #处理chatThreadNotFoundError的处理
def handle_exception(request: Request, exc: Exception):
    logger.error(f"处理异常, 请求路径: {request.url}, 异常信息: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "code": "400",
            "message": "会话不存在或者不属于当前用户"
        }
    )
