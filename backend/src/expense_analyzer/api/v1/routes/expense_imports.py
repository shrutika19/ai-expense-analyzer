from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import ValidationError

from expense_analyzer.api.v1.dependencies import (
    get_current_user,
    get_expense_import_service,
)
from expense_analyzer.domain.entities.user import User
from expense_analyzer.api.v1.schemas.expense_import import (
    ExpenseImportResponse,
)
from expense_analyzer.services.expense_import_service import (
    ExpenseImportService,
)
from expense_analyzer.exceptions.expense_import import (
    UnsupportedFileTypeException,
)

MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    ".csv": {"text/csv", "application/vnd.ms-excel"},
    ".json": {"application/json", "text/json"},
}


router = APIRouter(
    prefix="/expenses/import",
    tags=["Expense Import"],
)


@router.post(
    "",
    response_model=ExpenseImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_expenses(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ExpenseImportService = Depends(
        get_expense_import_service
    ),
) -> ExpenseImportResponse:
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileTypeException(suffix or "unknown")

    if file.content_type not in ALLOWED_MIME_TYPES[suffix]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "code": "UNSUPPORTED_MEDIA_TYPE",
                "message": (
                    f"MIME type '{file.content_type}' does not match "
                    f"the '{suffix}' file extension."
                ),
            },
        )

    temporary_file = NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        delete=False,
    )
    temporary_path = Path(temporary_file.name)

    try:
        total_size = 0
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail={
                        "code": "FILE_TOO_LARGE",
                        "message": (
                            "The uploaded file exceeds the 5 MiB limit."
                        ),
                    },
                )
            temporary_file.write(chunk)
        temporary_file.close()

        try:
            result = service.import_expenses_detailed(temporary_path,user_id=current_user.id,)
        except UnsupportedFileTypeException:
            raise
        except (ValueError, ValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid expense import data: {exc}",
            ) from exc

        return ExpenseImportResponse(
            imported_count=len(result.expenses),
            failed_count=len(result.errors),
            duplicate_count=result.skipped_duplicates,
            message=(
                "Expenses imported successfully."
                if not result.errors and not result.skipped_duplicates
                else "Import completed with skipped or invalid rows."
            ),
            errors=result.errors,
            skipped_rows=result.skipped_rows,
        )
    finally:
        if not temporary_file.closed:
            temporary_file.close()
        temporary_path.unlink(missing_ok=True)
        await file.close()