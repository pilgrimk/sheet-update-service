from app.config import settings
from app.models.payloads import SheetUpdateRequest
from app.services.mutation_planner import MutationPlanner
from app.services.sheet_structure_service import SheetStructureService
from app.services.sheet_writer import SheetWriter


class UpdateExecutionService:
    def __init__(self) -> None:
        self.structure_service = SheetStructureService()
        self.mutation_planner = MutationPlanner()
        self.writer = SheetWriter()

    def plan_only(self, payload: SheetUpdateRequest) -> dict:
        structure = self.structure_service.parse_structure()
        plan = self.mutation_planner.plan(structure, payload.records)

        return {
            "summary": {
                **plan["summary"],
                "structure_warnings": len(structure.get("warnings", [])),
            },
            "updates": plan["updates"],
            "missing_asins": plan["missing_asins"],
            "missing_weeks": plan["missing_weeks"],
            "planned_new_weeks": plan["planned_new_weeks"],
            "planned_new_asin_blocks": plan.get("planned_new_asin_blocks", []),
            "skipped_metrics": plan["skipped_metrics"],
            "warnings": plan["warnings"],
            "processed_records": plan["processed_records"],
            "structure_warnings": structure.get("warnings", []),
        }

    def apply_planned_updates_only(self, payload: SheetUpdateRequest) -> dict:
        structure = self.structure_service.parse_structure()
        plan = self.mutation_planner.plan(structure, payload.records)

        writer_result = self.writer.apply_updates(
            spreadsheet_id=settings.default_spreadsheet_id,
            worksheet_name=settings.default_worksheet_name,
            updates=plan["updates"],
            dry_run=settings.dry_run,
        )

        return {
            "summary": {
                **plan["summary"],
                "structure_warnings": len(structure.get("warnings", [])),
            },
            "writer_result": writer_result,
            "updates": plan["updates"],
            "missing_asins": plan["missing_asins"],
            "missing_weeks": plan["missing_weeks"],
            "planned_new_weeks": plan["planned_new_weeks"],
            "planned_new_asin_blocks": plan.get("planned_new_asin_blocks", []),
            "skipped_metrics": plan["skipped_metrics"],
            "warnings": plan["warnings"],
            "processed_records": plan["processed_records"],
            "structure_warnings": structure.get("warnings", []),
        }

    def apply_full_mutation_pipeline(self, payload: SheetUpdateRequest) -> dict:

        # 1. initial plan
        initial_structure = self.structure_service.parse_structure()
        initial_plan = self.mutation_planner.plan(initial_structure, payload.records)

        # 2. create weeks
        week_result = self.writer.create_week_columns(
            spreadsheet_id=settings.default_spreadsheet_id,
            worksheet_name=settings.default_worksheet_name,
            planned_new_weeks=initial_plan["planned_new_weeks"],
            dry_run=settings.dry_run,
        )

        # 3. create ASIN blocks
        asin_result = self.writer.create_asin_blocks(
            spreadsheet_id=settings.default_spreadsheet_id,
            worksheet_name=settings.default_worksheet_name,
            planned_new_asin_blocks=initial_plan.get("planned_new_asin_blocks", []),
            dry_run=settings.dry_run,
        )

        # 4. re-parse + re-plan
        refreshed_structure = self.structure_service.parse_structure()
        refreshed_plan = self.mutation_planner.plan(refreshed_structure, payload.records)

        # 5. apply updates
        update_result = self.writer.apply_updates(
            spreadsheet_id=settings.default_spreadsheet_id,
            worksheet_name=settings.default_worksheet_name,
            updates=refreshed_plan["updates"],
            dry_run=settings.dry_run,
        )

        return {
            "initial_summary": initial_plan["summary"],
            "week_creation_result": week_result,
            "asin_creation_result": asin_result,
            "refreshed_summary": refreshed_plan["summary"],
            "update_result": update_result,
        }

    def run_test_mutation(self, mode: str, payload: SheetUpdateRequest) -> dict:
        if mode == "plan_only":
            return self.plan_only(payload)

        if mode == "apply_existing_updates":
            return self.apply_planned_updates_only(payload)

        if mode == "apply_with_new_weeks":
            return self.apply_updates_with_new_weeks(payload)

        if mode == "apply_full":
            return self.apply_full_mutation_pipeline(payload)

        raise ValueError(f"Unsupported test mutation mode: {mode}")