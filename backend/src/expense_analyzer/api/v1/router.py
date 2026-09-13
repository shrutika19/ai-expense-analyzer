from fastapi import APIRouter

from expense_analyzer.api.v1.routes.analytics import (
    router as analytics_router,
)
from expense_analyzer.api.v1.routes.expenses import (
    router as expenses_router,
)
from expense_analyzer.api.v1.routes.expense_imports import (
    router as imports_router,
)
from expense_analyzer.api.v1.routes.auth import router as auth_router  


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(expenses_router)
router.include_router(analytics_router)
router.include_router(imports_router)
router.include_router(auth_router)