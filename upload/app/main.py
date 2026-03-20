import traceback
from fastapi import FastAPI, Header, HTTPException
from app.config import settings
from app.models.payloads import SheetUpdateRequest, TestMutationRequest
from app.services.sheet_access_service import SheetAccessService
from app.services.sheet_structure_service import SheetStructureService
from app.services.week_resolver import WeekResolver
from app.services.update_execution_service import UpdateExecutionService

app = FastAPI(title=settings.app_name)

sheet_access_service = SheetAccessService()
sheet_structure_service = SheetStructureService()
week_resolver = WeekResolver()
update_execution_service = UpdateExecutionService()


def require_api_key(x_api_key: str) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {
        "success": True,
        "app": settings.app_name,
        "env": settings.app_env,
        "dry_run": settings.dry_run,
        "require_year_in_week_headers": settings.require_year_in_week_headers,
        "allow_legacy_week_match": settings.allow_legacy_week_match,
    }


@app.get("/v1/sheet-access-test")
def sheet_access_test(x_api_key: str = Header(default="")):
    require_api_key(x_api_key)

    result = sheet_access_service.test_access()
    return {
        "success": True,
        "message": "Google Sheet access verified.",
        "data": result,
    }


@app.get("/v1/sheet-structure")
def sheet_structure(x_api_key: str = Header(default="")):
    require_api_key(x_api_key)

    result = sheet_structure_service.parse_structure()
    return {
        "success": True,
        "message": "Sheet structure parsed.",
        "data": result,
    }


@app.get("/v1/resolve-week")
def resolve_week(date: str, x_api_key: str = Header(default="")):
    require_api_key(x_api_key)

    structure = sheet_structure_service.parse_structure()
    week = week_resolver.resolve_week(date, structure["weeks"])

    return {
        "success": True,
        "input_date": date,
        "resolved_week": week,
        "structure_warnings": structure.get("warnings", []),
    }


@app.post("/v1/test-mutations")
def test_mutations(payload: TestMutationRequest, x_api_key: str = Header(default="")):
    require_api_key(x_api_key)

    sheet_payload = SheetUpdateRequest(records=payload.records)

    try:
        result = update_execution_service.run_test_mutation(payload.mode, sheet_payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print("\n=== UNHANDLED ERROR IN /v1/test-mutations ===")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "success": True,
        "message": f"Test mutation mode '{payload.mode}' processed.",
        "data": result,
    }