import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
    CategoryPredictionLowConfidenceException
)

from expense_analyzer.exceptions.expense_import import (
    UnsupportedFileTypeException,
)

from expense_analyzer.exceptions.auth import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
    InactiveUserException,
    InvalidTokenException,
)
from expense_analyzer.ml.exceptions import (
    ModelUnavailableError,
    PredictorUnavailableError,
)

logger = logging.getLogger(__name__)


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        },
    )

def expense_not_found_handler(
    request: Request,
    exc: ExpenseNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "EXPENSE_NOT_FOUND",
                "message": str(exc),
            }
        },
    )


def unsupported_file_type_handler(
    request: Request,
    exc: UnsupportedFileTypeException,
) -> JSONResponse:
    return JSONResponse(
        status_code=415,
        content={
            "error": {
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": str(exc),
            }
        },
    )

async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsException,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": "USER_ALREADY_EXISTS",
            "message": str(exc),
        },
    )


async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsException,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "error": "INVALID_CREDENTIALS",
            "message": str(exc),
        },
    )


async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": "USER_NOT_FOUND",
            "message": str(exc),
        },
    )


async def inactive_user_handler(
    request: Request,
    exc: InactiveUserException,
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "error": "INACTIVE_USER",
            "message": str(exc),
        },
    )


async def invalid_token_handler(
    request: Request,
    exc: InvalidTokenException,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "error": "INVALID_TOKEN",
            "message": str(exc),
        },
    )



async def model_unavailable_handler(
    request: Request,
    exc: ModelUnavailableError,
) -> JSONResponse:
    logger.exception(
        "ML model unavailable: %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "MODEL_UNAVAILABLE",
                "message": "ML model is currently unavailable.",
            }
        },
    )


async def predictor_unavailable_handler(
    request: Request,
    exc: PredictorUnavailableError,
) -> JSONResponse:
    logger.exception(
        "ML predictor unavailable: %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "PREDICTOR_UNAVAILABLE",
                "message": "Prediction could not be completed.",
            }
        },
    )


async def category_prediction_low_confidence_handler(
    request: Request,
    exc: CategoryPredictionLowConfidenceException,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "CATEGORY_PREDICTION_LOW_CONFIDENCE",
                "message": (
                    "Category could not be predicted with "
                    "sufficient confidence. Please provide a category."
                ),
            }
        },
    )
