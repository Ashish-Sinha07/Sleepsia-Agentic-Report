"""Run manager for tracking and persisting workflow execution state."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .models import RunState, RunStatus, RunResult, WorkflowStage, StageStatus, StageResult


class RunManager:
    """Manages workflow run state, checkpoints, and persistence."""

    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        """
        Initialize run manager.

        Args:
            checkpoint_dir: Directory for persisting run state
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._runs: Dict[str, RunState] = {}

    def create_run(self, workflow_id: str, business_date: str) -> RunState:
        """
        Create a new workflow run.

        Args:
            workflow_id: Workflow identifier
            business_date: Date for this run

        Returns:
            New RunState object
        """
        run = RunState(workflow_id=workflow_id, business_date=business_date)
        run.start_time = datetime.utcnow()
        run.status = RunStatus.PENDING
        self._runs[run.run_id] = run
        self._save_checkpoint(run)
        return run

    def get_run(self, run_id: str) -> Optional[RunState]:
        """Get run state by run_id."""
        if run_id in self._runs:
            return self._runs[run_id]
        return self._load_checkpoint(run_id)

    def update_run_status(self, run_id: str, status: RunStatus,
                         error_message: Optional[str] = None):
        """Update overall run status."""
        run = self.get_run(run_id)
        if run:
            run.status = status
            if error_message:
                run.error_message = error_message
            self._save_checkpoint(run)

    def record_stage_result(self, run_id: str, result: StageResult):
        """Record the result of a stage execution."""
        run = self.get_run(run_id)
        if run:
            run.stage_results[result.stage] = result
            if result.status == StageStatus.SUCCESS:
                run.checkpoints[result.stage] = datetime.utcnow()
            if result.idempotency_key:
                run.idempotency_keys[result.stage] = result.idempotency_key
            self._save_checkpoint(run)

    def complete_run(self, run_id: str) -> RunResult:
        """Complete a run and return final result."""
        run = self.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        run.end_time = datetime.utcnow()
        if run.start_time:
            run.duration_seconds = (run.end_time - run.start_time).total_seconds()

        self._save_checkpoint(run)
        return RunResult.from_run_state(run)

    def mark_failed_source(self, run_id: str, source: str):
        """Mark a required data source as failed."""
        run = self.get_run(run_id)
        if run and source not in run.failed_sources:
            run.failed_sources.append(source)
            self._save_checkpoint(run)

    def mark_partial_source(self, run_id: str, source: str):
        """Mark an optional data source as partially available."""
        run = self.get_run(run_id)
        if run and source not in run.partial_sources:
            run.partial_sources.append(source)
            self._save_checkpoint(run)

    def get_last_successful_stage(self, run_id: str) -> Optional[WorkflowStage]:
        """Get the last stage that completed successfully."""
        run = self.get_run(run_id)
        return run.get_last_successful_stage() if run else None

    def can_resume(self, run_id: str) -> bool:
        """Check if a run can be resumed from last successful stage."""
        run = self.get_run(run_id)
        if not run:
            return False
        last_stage = run.get_last_successful_stage()
        return last_stage is not None

    def list_runs(self) -> list:
        """List all runs (from in-memory cache)."""
        return list(self._runs.values())

    def _save_checkpoint(self, run: RunState):
        """Persist run state to disk."""
        checkpoint_path = self.checkpoint_dir / f"{run.run_id}.json"
        checkpoint_data = {
            "run_id": run.run_id,
            "workflow_id": run.workflow_id,
            "business_date": run.business_date,
            "status": run.status.value,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "duration_seconds": run.duration_seconds,
            "failed_sources": run.failed_sources,
            "partial_sources": run.partial_sources,
            "error_message": run.error_message,
            "metadata": run.metadata,
            "stage_results": {
                stage.value: {
                    "stage": stage.value,
                    "status": result.status.value,
                    "start_time": result.start_time.isoformat(),
                    "end_time": result.end_time.isoformat() if result.end_time else None,
                    "duration_seconds": result.duration_seconds,
                    "attempt": result.attempt,
                    "error_message": result.error_message,
                    "error_type": result.error_type,
                    "warning_messages": result.warning_messages,
                    "idempotency_key": result.idempotency_key,
                }
                for stage, result in run.stage_results.items()
            },
            "checkpoints": {
                stage.value: ts.isoformat() for stage, ts in run.checkpoints.items()
            },
            "idempotency_keys": run.idempotency_keys,
        }
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def _load_checkpoint(self, run_id: str) -> Optional[RunState]:
        """Load run state from disk."""
        checkpoint_path = self.checkpoint_dir / f"{run_id}.json"
        if not checkpoint_path.exists():
            return None

        with open(checkpoint_path, "r") as f:
            data = json.load(f)

        run = RunState(
            run_id=data["run_id"],
            workflow_id=data["workflow_id"],
            business_date=data["business_date"],
            status=RunStatus(data["status"]),
            failed_sources=data.get("failed_sources", []),
            partial_sources=data.get("partial_sources", []),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )

        if data["start_time"]:
            run.start_time = datetime.fromisoformat(data["start_time"])
        if data["end_time"]:
            run.end_time = datetime.fromisoformat(data["end_time"])
        run.duration_seconds = data.get("duration_seconds")

        for stage_name, result_data in data.get("stage_results", {}).items():
            stage = WorkflowStage(stage_name)
            result = StageResult(
                stage=stage,
                status=StageStatus(result_data["status"]),
                start_time=datetime.fromisoformat(result_data["start_time"]),
                attempt=result_data["attempt"],
                error_message=result_data.get("error_message"),
                error_type=result_data.get("error_type"),
                warning_messages=result_data.get("warning_messages", []),
                idempotency_key=result_data.get("idempotency_key"),
            )
            if result_data.get("end_time"):
                result.end_time = datetime.fromisoformat(result_data["end_time"])
            result.duration_seconds = result_data.get("duration_seconds")
            run.stage_results[stage] = result

        run.idempotency_keys = data.get("idempotency_keys", {})
        self._runs[run_id] = run
        return run
