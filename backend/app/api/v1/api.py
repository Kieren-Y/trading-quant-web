from fastapi import APIRouter

from app.api.v1 import asset, exchange, order, strategy

api_router = APIRouter()


@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


api_router.include_router(exchange.router, prefix="/exchanges", tags=["exchanges"])
api_router.include_router(asset.router, prefix="/assets", tags=["assets"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])
