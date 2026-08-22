"""Main workflow orchestrator for the reporting pipeline."""

import time
from datetime import date, datetime
from typing import Dict, Optional, Any

from .models import (
    WorkflowStage,
    StageStatus,
    RunStatus,
    SourceRequirement,
    WorkflowDefinition,
    RunState,
    StageResult,
    RunResult,
)
from .service_interfaces import (
    IngestionService,
    ValidationService,
    MetricService,
    AnalysisService,
    InsightService,
    ReportService,
    DistributionService,
    MonitoringService,
)
from .run_manager import RunManager
from .idempotency import IdempotencyKeyManager, IdempotencyCache


class WorkflowOrchestrator:
    """Deterministic workflow orchestrator for the reporting pipeline."""

    def __init__(
        self,
        workflow_definition: WorkflowDefinition,
        ingestion_service: IngestionService,
        validation_service: ValidationService,
        metric_service: MetricService,
        analysis_service: AnalysisService,
        insight_service: InsightService,
        report_service: ReportService,
        distribution_service: DistributionService,
        monitoring_service: MonitoringService,
        run_manager: Optional[RunManager] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            workflow_definition: Workflow definition with stages and config
            ingestion_service: Service for data ingestion
            validation_service: Service for data validation
            metric_service: Service for metric calculation
            analysis_service: Service for analysis
            insight_service: Service for insight generation
            report_service: Service for report generation
            distribution_service: Service for report distribution
            monitoring_service: Service for audit and monitoring
            run_manager: Optional run manager for persistence
        """
        self.workflow_def = workflow_definition
        self.ingestion = ingestion_service
        self.validation = validation_service
        self.metrics = metric_service
        self.analysis = analysis_service
        self.insights = insight_service
        self.reports = report_service
        self.distribution = distribution_service
        self.monitoring = monitoring_service
        self.run_manager = run_manager or RunManager()
        self.idempotency_cache = IdempotencyCache()

    def execute(self, business_date: date, resume_run_id: Optional[str] = None) -> RunResult:
        """
        Execute the complete workflow pipeline.

        Args:
            business_date: Date to run the pipeline for
            resume_run_id: Optional run ID to resume from checkpoint

        Returns:
            RunResult with complete execution information
        """
        if resume_run_id:
            run = self.run_manager.get_run(resume_run_id)
            if not run:
                raise ValueError(f"Run {resume_run_id} not found")
        else:
            run = self.run_manager.create_run(self.workflow_def.workflow_id,
                                             business_date.isoformat())

        run.status = RunStatus.RUNNING
        self.run_manager.update_run_status(run.run_id, RunStatus.RUNNING)

        try:
            # Execute each stage in sequence
            for stage in self.workflow_def.stages:
                # Skip already successful stages if resuming
                if resume_run_id and stage in run.stage_results:
                    if run.stage_results[stage].status == StageStatus.SUCCESS:
                        continue

                success = self._execute_stage(run, stage, business_date)
                if not success:
                    break

            # Determine final status
            if run.status == RunStatus.RUNNING:
                # Check if any required stage failed
                has_required_failure = any(
                    stage_result.status == StageStatus.FAILED
                    for stage, stage_result in run.stage_results.items()
                    if not self._is_optional_stage(stage)
                )

                if has_required_failure:
                    run.status = RunStatus.FAILED
                    failed_stages = [
                        s.value for s, r in run.stage_results.items()
                        if r.status == StageStatus.FAILED and not self._is_optional_stage(s)
                    ]
                    run.error_message = f"Required stages failed: {', '.join(failed_stages)}"
                elif run.failed_sources:
                    run.status = RunStatus.FAILED
                    run.error_message = f"Required sources failed: {', '.join(run.failed_sources)}"
                elif run.partial_sources or any(
                    stage_result.status == StageStatus.WARNING
                    for stage_result in run.stage_results.values()
                ):
                    run.status = RunStatus.PARTIAL
                    messages = []
                    if run.partial_sources:
                        messages.append(f"sources: {', '.join(run.partial_sources)}")
                    warnings = [
                        s.value for s, r in run.stage_results.items()
                        if r.status == StageStatus.WARNING
                    ]
                    if warnings:
                        messages.append(f"stages: {', '.join(warnings)}")
                    run.error_message = f"Optional unavailable ({', '.join(messages)})"
                else:
                    run.status = RunStatus.SUCCESS

        except Exception as e:
            run.status = RunStatus.FAILED
            run.error_message = str(e)

        return self.run_manager.complete_run(run.run_id)

    def resume(self, run_id: str) -> RunResult:
        """
        Resume a failed workflow from the last successful stage.

        Args:
            run_id: Run ID to resume

        Returns:
            RunResult with complete execution information
        """
        run = self.run_manager.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        if not self.run_manager.can_resume(run_id):
            raise ValueError(f"Run {run_id} cannot be resumed - no successful stages")

        business_date = date.fromisoformat(run.business_date)
        return self.execute(business_date, resume_run_id=run_id)

    def _execute_stage(self, run: RunState, stage: WorkflowStage, business_date: date) -> bool:
        """
        Execute a single stage with retry logic.

        Args:
            run: Current run state
            stage: Stage to execute
            business_date: Date for this run

        Returns:
            True if stage succeeded or was skipped, False if it failed fatally
        """
        # Generate idempotency key
        idempotency_key = self._get_idempotency_key(stage, business_date)

        # Check idempotency cache
        if self.workflow_def.idempotency_enabled:
            cached_result = self.idempotency_cache.get(idempotency_key)
            if cached_result:
                result = StageResult(
                    stage=stage,
                    status=StageStatus.SUCCESS,
                    start_time=datetime.utcnow(),
                    output_data=cached_result,
                    idempotency_key=idempotency_key,
                    attempt=1,
                )
                result.set_success(cached_result)
                run.stage_results[stage] = result
                self.run_manager.record_stage_result(run.run_id, result)
                return True

        # Try to execute with retries
        max_retries = self.workflow_def.retry_policy.max_retries
        for attempt in range(1, max_retries + 1):
            result = StageResult(
                stage=stage,
                status=StageStatus.RUNNING,
                start_time=datetime.utcnow(),
                attempt=attempt,
                idempotency_key=idempotency_key,
            )

            try:
                # Get output from previous stage
                stage_input = self._get_stage_input(run, stage)

                # Execute stage
                output = self._execute_stage_handler(stage, stage_input, idempotency_key)

                # Cache result if idempotency enabled
                if self.workflow_def.idempotency_enabled:
                    self.idempotency_cache.set(idempotency_key, output)

                result.set_success(output)
                run.stage_results[stage] = result
                self.run_manager.record_stage_result(run.run_id, result)
                return True

            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__

                if attempt < max_retries:
                    # Retry with backoff
                    delay = self.workflow_def.retry_policy.get_delay_for_attempt(attempt)
                    time.sleep(delay)
                else:
                    # Final attempt failed - determine if fatal
                    is_optional = self._is_optional_stage(stage)

                    if is_optional:
                        result.set_warning(error_msg)
                        run.stage_results[stage] = result
                        self.run_manager.record_stage_result(run.run_id, result)
                        # Mark as partial run
                        run.mark_partial(f"Optional stage {stage.value} failed")
                        return True
                    else:
                        result.set_failure(error_msg, error_type)
                        run.stage_results[stage] = result
                        self.run_manager.record_stage_result(run.run_id, result)
                        return False

        return False

    def _execute_stage_handler(self, stage: WorkflowStage, stage_input: Dict[str, Any],
                              idempotency_key: str) -> Dict[str, Any]:
        """Execute the appropriate stage handler."""
        if stage == WorkflowStage.INGESTION:
            return self.ingestion.ingest(date.today(), idempotency_key)
        elif stage == WorkflowStage.VALIDATION:
            return self.validation.validate(stage_input, idempotency_key)
        elif stage == WorkflowStage.METRICS:
            return self.metrics.calculate_metrics(stage_input, idempotency_key)
        elif stage == WorkflowStage.ANALYSIS:
            return self.analysis.analyze(stage_input, idempotency_key)
        elif stage == WorkflowStage.INSIGHTS:
            return self.insights.generate_insights(stage_input, idempotency_key)
        elif stage == WorkflowStage.REPORT:
            return self.reports.generate_report(stage_input, idempotency_key)
        elif stage == WorkflowStage.DISTRIBUTION:
            return self.distribution.distribute(stage_input, idempotency_key)
        elif stage == WorkflowStage.AUDIT:
            workflow_state = self._build_workflow_state(stage_input)
            return self.monitoring.audit(workflow_state, idempotency_key)
        else:
            raise ValueError(f"Unknown stage: {stage}")

    def _get_stage_input(self, run: RunState, stage: WorkflowStage) -> Dict[str, Any]:
        """Get input data for a stage from previous stage results."""
        if stage == WorkflowStage.INGESTION:
            return {}

        # Find the output from the previous stage
        for prev_stage in self.workflow_def.stages:
            if prev_stage == stage:
                break
            if prev_stage in run.stage_results:
                result = run.stage_results[prev_stage]
                if result.status in (StageStatus.SUCCESS, StageStatus.WARNING):
                    return result.output_data

        return {}

    def _get_idempotency_key(self, stage: WorkflowStage, business_date: date) -> str:
        """Generate idempotency key for a stage."""
        if stage == WorkflowStage.INGESTION:
            return IdempotencyKeyManager.generate_ingestion_key(business_date)
        elif stage == WorkflowStage.VALIDATION:
            return IdempotencyKeyManager.generate_validation_key(business_date)
        elif stage == WorkflowStage.METRICS:
            return IdempotencyKeyManager.generate_metrics_key(business_date)
        elif stage == WorkflowStage.ANALYSIS:
            return IdempotencyKeyManager.generate_analysis_key(business_date)
        elif stage == WorkflowStage.INSIGHTS:
            return IdempotencyKeyManager.generate_insights_key(business_date)
        elif stage == WorkflowStage.REPORT:
            return IdempotencyKeyManager.generate_report_key(business_date)
        elif stage == WorkflowStage.DISTRIBUTION:
            return IdempotencyKeyManager.generate_distribution_key(business_date)
        elif stage == WorkflowStage.AUDIT:
            return IdempotencyKeyManager.generate_audit_key(business_date)
        else:
            raise ValueError(f"Unknown stage: {stage}")

    def _is_optional_stage(self, stage: WorkflowStage) -> bool:
        """Check if a stage is optional (skippable on failure)."""
        # Distribution and audit are optional
        return stage in (WorkflowStage.DISTRIBUTION, WorkflowStage.AUDIT)

    def _build_workflow_state(self, audit_input: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete workflow state for audit."""
        return audit_input or {}
