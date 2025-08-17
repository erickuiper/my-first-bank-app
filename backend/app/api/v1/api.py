from fastapi import APIRouter

from app.api.v1.endpoints import accounts, allowance_rules, auth, children, chores

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(allowance_rules.router, tags=["allowance"])
api_router.include_router(chores.router, tags=["chores"])
