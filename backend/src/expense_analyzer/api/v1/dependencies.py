from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from expense_analyzer.analytics.calculators.category import (
    CategoryCalculator,
)
from expense_analyzer.analytics.calculators.monthly import (
    MonthlyCalculator,
)
from expense_analyzer.analytics.calculators.summary import (
    SummaryCalculator,
)
from expense_analyzer.analytics.service import AnalyticsService
from expense_analyzer.domain.entities.user import User
from expense_analyzer.exceptions.auth import (
    InvalidCredentialsException,
)
from expense_analyzer.preprocessing.pipeline import (
    PreprocessingPipeline,
)
from expense_analyzer.preprocessing.processors.amount import (
    AmountNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.date import (
    DateNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.duplicate import (
    DuplicateDetectionProcessor,
)
from expense_analyzer.preprocessing.processors.missing_value import (
    MissingValueProcessor,
)
from expense_analyzer.preprocessing.processors.normalization import (
    NormalizationProcessor,
)
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.repositories.user_repository import (
    UserRepository,
)
from expense_analyzer.security.jwt import JWTService
from expense_analyzer.services.auth_service import AuthService
from expense_analyzer.services.expense_import_service import (
    ExpenseImportService,
)
from expense_analyzer.services.expense_service import ExpenseService
from expense_analyzer.core.config import get_settings
from expense_analyzer.ml.inference.service import InferenceService
from functools import lru_cache

bearer_scheme = HTTPBearer()


def get_jwt_service() -> JWTService:
    return JWTService()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    jwt_service: JWTService = Depends(
        get_jwt_service
    ),
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
) -> User:

    token = credentials.credentials

    user_id = jwt_service.decode_access_token(token)

    user = user_repository.find_by_id(user_id)

    if user is None:
        raise InvalidCredentialsException(
            "Invalid credentials"
        )

    if not user.is_active:
        raise InvalidCredentialsException(
            "Invalid credentials"
        )

    return user


def get_preprocessing_pipeline() -> PreprocessingPipeline:
    return PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )


def get_expense_repository() -> ExpenseRepository:
    return ExpenseRepository()


def get_expense_service(
    pipeline: PreprocessingPipeline = Depends(
        get_preprocessing_pipeline
    ),
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
) -> ExpenseService:
    return ExpenseService(
        preprocessing_pipeline=pipeline,
        repository=repository,
    )


def get_analytics_service(
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
) -> AnalyticsService:
    return AnalyticsService(
        summary_calculator=SummaryCalculator(),
        category_calculator=CategoryCalculator(),
        monthly_calculator=MonthlyCalculator(),
        repository=repository,
    )


def get_expense_import_service(
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
    pipeline: PreprocessingPipeline = Depends(
        get_preprocessing_pipeline
    ),
) -> ExpenseImportService:
    return ExpenseImportService(
        repository=repository,
        preprocessing_pipeline=pipeline,
    )


def get_auth_service(
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
    jwt_service: JWTService = Depends(
        get_jwt_service
    ),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        jwt_service=jwt_service,
    )


@lru_cache
def get_inference_service() -> InferenceService:
    settings = get_settings()

    return InferenceService(
        artifacts_directory=settings.model_artifacts_directory,
        model_version=settings.model_version,
    )