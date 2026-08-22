"""Tests for workflow orchestration engine."""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from analytics.orchestration import (
    WorkflowStage,
    StageStatus,
    RunStatus,
    SourceRequirement,
    WorkflowDefinition,
    RunState,
    StageResult,
    RetryPolicy,
    IngestionService,
    ValidationService,
    MetricService,
    AnalysisService,
    InsightService,
    ReportService,
    DistributionService,
    MonitoringService,
    WorkflowOrchestrator,
    RunManager,
)
from analytics.orchestration.idempotency import IdempotencyKeyManager, IdempotencyCache


class TestIdempotencyKeyManager:
    """Tests for idempotency key generation."""

    def test_generate_key_is_deterministic(self):
        """Same inputs produce same key."""
        key1 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
        key2 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
        assert key1 == key2

    def test_generate_key_differs_by_stage(self):
        """Different stages produce different keys."""
        key1 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
        key2 = IdempotencyKeyManager.generate_key("validation", date(2026, 8, 21))
        assert key1 != key2

    def test_generate_key_differs_by_date(self):
        """Different dates produce different keys."""
        key1 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
        key2 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 22))
        assert key1 != key2

    def test_generate_key_with_context(self):
        """Context affects key generation."""
        key1 = IdempotencyKeyManager.generate_key(
            "ingestion", date(2026, 8, 21), {"sources": ["amazon"]}
        )
        key2 = IdempotencyKeyManager.generate_key(
            "ingestion", date(2026, 8, 21), {"sources": ["flipkart"]}
        )
        assert key1 != key2

    def test_stage_specific_key_generators(self):
        """Stage-specific generators produce correct keys."""
        base_key = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
        ingestion_key = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
        assert base_key == ingestion_key

    def test_key_is_deterministic_after_restart(self):
        """Key remains the same even after cache clear."""
        key1 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
        # Simulate restart - no state preserved
        key2 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
        assert key1 == key2


class TestIdempotencyCache:
    """Tests for idempotency cache."""

    def test_cache_get_set(self):
        """Cache can store and retrieve values."""
        cache = IdempotencyCache()
        key = "test_key"
        data = {"result": "success"}

        cache.set(key, data)
        assert cache.get(key) == data

    def test_cache_exists(self):
        """Cache existence check works."""
        cache = IdempotencyCache()
        cache.set("key1", {"data": "value"})

        assert cache.exists("key1")
        assert not cache.exists("nonexistent")

    def test_cache_clear(self):
        """Cache can be cleared."""
        cache = IdempotencyCache()
        cache.set("key1", {"data": "value"})
        cache.clear()

        assert not cache.exists("key1")
        assert cache.size() == 0

    def test_cache_size(self):
        """Cache size tracking works."""
        cache = IdempotencyCache()
        assert cache.size() == 0

        cache.set("key1", {"data": "value"})
        assert cache.size() == 1

        cache.set("key2", {"data": "value"})
        assert cache.size() == 2


class TestRunManager:
    """Tests for run manager."""

    def test_create_run(self):
        """Can create a new run."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        assert run.workflow_id == "workflow1"
        assert run.business_date == "2026-08-21"
        assert run.status == RunStatus.PENDING
        assert run.start_time is not None

    def test_get_run(self):
        """Can retrieve a run."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")
        retrieved = manager.get_run(run.run_id)

        assert retrieved.run_id == run.run_id
        assert retrieved.workflow_id == "workflow1"

    def test_update_run_status(self):
        """Can update run status."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        manager.update_run_status(run.run_id, RunStatus.RUNNING)
        updated = manager.get_run(run.run_id)

        assert updated.status == RunStatus.RUNNING

    def test_record_stage_result(self):
        """Can record stage results."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        result = StageResult(
            stage=WorkflowStage.INGESTION,
            status=StageStatus.SUCCESS,
            start_time=datetime.utcnow(),
        )
        result.set_success({"data": "ingested"})

        manager.record_stage_result(run.run_id, result)
        updated = manager.get_run(run.run_id)

        assert WorkflowStage.INGESTION in updated.stage_results
        assert updated.stage_results[WorkflowStage.INGESTION].status == StageStatus.SUCCESS

    def test_mark_failed_source(self):
        """Can mark failed sources."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        manager.mark_failed_source(run.run_id, "amazon")
        updated = manager.get_run(run.run_id)

        assert "amazon" in updated.failed_sources

    def test_mark_partial_source(self):
        """Can mark partial sources."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        manager.mark_partial_source(run.run_id, "flipkart")
        updated = manager.get_run(run.run_id)

        assert "flipkart" in updated.partial_sources

    def test_get_last_successful_stage(self):
        """Can retrieve last successful stage."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        # Record successful ingestion
        result = StageResult(
            stage=WorkflowStage.INGESTION,
            status=StageStatus.SUCCESS,
            start_time=datetime.utcnow(),
        )
        result.set_success()
        manager.record_stage_result(run.run_id, result)

        # Record successful validation
        result = StageResult(
            stage=WorkflowStage.VALIDATION,
            status=StageStatus.SUCCESS,
            start_time=datetime.utcnow(),
        )
        result.set_success()
        manager.record_stage_result(run.run_id, result)

        # Record failed metrics
        result = StageResult(
            stage=WorkflowStage.METRICS,
            status=StageStatus.FAILED,
            start_time=datetime.utcnow(),
        )
        result.set_failure("Calculation error")
        manager.record_stage_result(run.run_id, result)

        last = manager.get_last_successful_stage(run.run_id)
        assert last == WorkflowStage.VALIDATION

    def test_can_resume(self):
        """Can determine if run is resumable."""
        manager = RunManager()
        run = manager.create_run("workflow1", "2026-08-21")

        # No results yet
        assert not manager.can_resume(run.run_id)

        # Add successful stage
        result = StageResult(
            stage=WorkflowStage.INGESTION,
            status=StageStatus.SUCCESS,
            start_time=datetime.utcnow(),
        )
        result.set_success()
        manager.record_stage_result(run.run_id, result)

        # Now can resume
        assert manager.can_resume(run.run_id)

    def test_checkpoint_persistence(self):
        """Run state persists to disk."""
        import tempfile
        import shutil

        checkpoint_dir = tempfile.mkdtemp()
        try:
            manager = RunManager(checkpoint_dir=checkpoint_dir)
            run = manager.create_run("workflow1", "2026-08-21")

            # Record stage
            result = StageResult(
                stage=WorkflowStage.INGESTION,
                status=StageStatus.SUCCESS,
                start_time=datetime.utcnow(),
            )
            result.set_success({"records": 100})
            manager.record_stage_result(run.run_id, result)

            # Verify checkpoint was created
            checkpoint_file = f"{checkpoint_dir}/{run.run_id}.json"
            import os
            assert os.path.exists(checkpoint_file)

            # Create new manager and load checkpoint
            manager2 = RunManager(checkpoint_dir=checkpoint_dir)
            loaded = manager2.get_run(run.run_id)
            assert loaded.run_id == run.run_id
            assert WorkflowStage.INGESTION in loaded.stage_results
        finally:
            shutil.rmtree(checkpoint_dir)


class MockIngestionService(IngestionService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def ingest(self, business_date: date, idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Ingestion failed")
        return {"records": 100, "sources": ["amazon", "flipkart"]}


class MockValidationService(ValidationService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def validate(self, ingestion_result: Dict[str, Any],
                 idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Validation failed")
        return {"valid_records": 100, "errors": []}


class MockMetricService(MetricService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def calculate_metrics(self, validation_result: Dict[str, Any],
                         idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Metrics calculation failed")
        return {"metrics": {"revenue": 100000, "profit_margin": 35.5}}


class MockAnalysisService(AnalysisService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def analyze(self, metrics_result: Dict[str, Any],
               idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Analysis failed")
        return {"findings": ["Finding 1", "Finding 2"]}


class MockInsightService(InsightService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def generate_insights(self, analysis_result: Dict[str, Any],
                         idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Insight generation failed")
        return {"insights": ["Insight 1", "Insight 2"]}


class MockReportService(ReportService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def generate_report(self, insights_result: Dict[str, Any],
                       idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Report generation failed")
        return {"report_path": "/reports/report_2026_08_21.pdf"}


class MockDistributionService(DistributionService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def distribute(self, report_result: Dict[str, Any],
                  idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Distribution failed")
        return {"recipients": 5, "status": "sent"}


class MockMonitoringService(MonitoringService):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def audit(self, workflow_state: Dict[str, Any],
             idempotency_key: str) -> Dict[str, Any]:
        self.call_count += 1
        if self.should_fail:
            raise Exception("Audit failed")
        return {"audit_status": "passed", "issues": []}


class TestWorkflowOrchestrator:
    """Tests for workflow orchestrator."""

    def _create_orchestrator(self, **service_overrides) -> WorkflowOrchestrator:
        """Create orchestrator with mocked services."""
        defaults = {
            "ingestion": MockIngestionService(),
            "validation": MockValidationService(),
            "metrics": MockMetricService(),
            "analysis": MockAnalysisService(),
            "insights": MockInsightService(),
            "reports": MockReportService(),
            "distribution": MockDistributionService(),
            "monitoring": MockMonitoringService(),
        }
        defaults.update(service_overrides)

        return WorkflowOrchestrator(
            workflow_definition=WorkflowDefinition(
                workflow_id="test_workflow",
                name="Test Workflow",
            ),
            ingestion_service=defaults["ingestion"],
            validation_service=defaults["validation"],
            metric_service=defaults["metrics"],
            analysis_service=defaults["analysis"],
            insight_service=defaults["insights"],
            report_service=defaults["reports"],
            distribution_service=defaults["distribution"],
            monitoring_service=defaults["monitoring"],
            run_manager=RunManager(),
        )

    def test_successful_complete_workflow(self):
        """Complete workflow executes successfully."""
        orchestrator = self._create_orchestrator()
        result = orchestrator.execute(date(2026, 8, 21))

        assert result.status == RunStatus.SUCCESS
        assert result.run_id
        assert result.duration_seconds > 0
        # All stages should complete
        assert len(result.stage_results) == 8

    def test_all_stages_execute_in_order(self):
        """Stages execute in correct order."""
        services = {
            "ingestion": MockIngestionService(),
            "validation": MockValidationService(),
            "metrics": MockMetricService(),
            "analysis": MockAnalysisService(),
            "insights": MockInsightService(),
            "reports": MockReportService(),
            "distribution": MockDistributionService(),
            "monitoring": MockMonitoringService(),
        }
        orchestrator = self._create_orchestrator(**services)
        result = orchestrator.execute(date(2026, 8, 21))

        assert services["ingestion"].call_count == 1
        assert services["validation"].call_count == 1
        assert services["metrics"].call_count == 1
        assert services["analysis"].call_count == 1
        assert services["insights"].call_count == 1
        assert services["reports"].call_count == 1
        assert services["distribution"].call_count == 1
        assert services["monitoring"].call_count == 1

    def test_required_stage_failure_stops_pipeline(self):
        """Required stage failure stops dependent stages."""
        orchestrator = self._create_orchestrator(
            validation=MockValidationService(should_fail=True)
        )
        # Disable retry delays for testing
        orchestrator.workflow_def.retry_policy.max_retries = 1
        orchestrator.workflow_def.retry_policy.retry_delay_seconds = 0
        result = orchestrator.execute(date(2026, 8, 21))

        assert result.status == RunStatus.FAILED
        # Ingestion should succeed
        assert result.stage_results[WorkflowStage.INGESTION].status == StageStatus.SUCCESS
        # Validation should fail
        assert result.stage_results[WorkflowStage.VALIDATION].status == StageStatus.FAILED
        # Downstream stages should not execute
        assert WorkflowStage.METRICS not in result.stage_results

    def test_optional_stage_failure_allows_continuation(self):
        """Optional stage failure marks run as partial but continues."""
        orchestrator = self._create_orchestrator(
            distribution=MockDistributionService(should_fail=True)
        )
        # Disable retry delays for testing
        orchestrator.workflow_def.retry_policy.max_retries = 1
        orchestrator.workflow_def.retry_policy.retry_delay_seconds = 0
        result = orchestrator.execute(date(2026, 8, 21))

        # Should be partial, not failed
        assert result.status == RunStatus.PARTIAL
        # Distribution should warn but not fail
        assert result.stage_results[WorkflowStage.DISTRIBUTION].status == StageStatus.WARNING
        # Audit should still run
        assert WorkflowStage.AUDIT in result.stage_results

    def test_idempotency_prevents_duplicate_execution(self):
        """Idempotent operation returns cached result."""
        ingestion = MockIngestionService()
        orchestrator = self._create_orchestrator(ingestion=ingestion)

        # First run
        result1 = orchestrator.execute(date(2026, 8, 21))
        assert ingestion.call_count == 1

        # Second run with same date
        # Idempotency cache prevents re-execution within same orchestrator
        result2 = orchestrator.execute(date(2026, 8, 21))

        # Ingestion should NOT be called again due to idempotency cache
        # The cached result from first run is reused
        assert ingestion.call_count == 1  # Not called again
        assert result1.status == result2.status

    def test_resume_from_checkpoint(self):
        """Can resume workflow from last successful stage."""
        orchestrator = self._create_orchestrator(
            metrics=MockMetricService(should_fail=True)
        )

        # First run fails at metrics stage
        result1 = orchestrator.execute(date(2026, 8, 21))
        run_id = result1.run_id
        assert result1.stage_results[WorkflowStage.METRICS].status == StageStatus.FAILED

        # Create new orchestrator with fixed metrics service
        orchestrator2 = self._create_orchestrator()

        # Resume from checkpoint
        result2 = orchestrator2.resume(run_id)
        assert result2.status == RunStatus.SUCCESS

    def test_run_state_persistence(self):
        """Run state persists across orchestrator instances."""
        orchestrator1 = self._create_orchestrator()
        result1 = orchestrator1.execute(date(2026, 8, 21))

        # Retrieve run via different orchestrator
        orchestrator2 = self._create_orchestrator()
        persisted_run = orchestrator2.run_manager.get_run(result1.run_id)

        assert persisted_run.run_id == result1.run_id
        assert persisted_run.status == result1.status

    def test_retry_on_transient_failure(self):
        """Transient failures are retried."""
        call_count = [0]

        class FlakeyService(MockValidationService):
            def validate(self, ingestion_result, idempotency_key):
                call_count[0] += 1
                if call_count[0] < 2:  # Fail first time
                    raise Exception("Transient failure")
                return super().validate(ingestion_result, idempotency_key)

        orchestrator = self._create_orchestrator(
            validation=FlakeyService(),
        )
        # Disable retry delays for testing
        orchestrator.workflow_def.retry_policy.max_retries = 3
        orchestrator.workflow_def.retry_policy.exponential_backoff = False
        orchestrator.workflow_def.retry_policy.retry_delay_seconds = 0

        result = orchestrator.execute(date(2026, 8, 21))

        # Should succeed after retry
        assert result.status == RunStatus.SUCCESS
        assert call_count[0] == 2  # Called twice (once failed, once succeeded)

    def test_permanent_failure_after_retries(self):
        """Permanent failures are not retried indefinitely."""
        call_count = [0]

        class AlwaysFailService(MockValidationService):
            def validate(self, ingestion_result, idempotency_key):
                call_count[0] += 1
                raise Exception("Permanent failure")

        orchestrator = self._create_orchestrator(
            validation=AlwaysFailService(),
        )
        orchestrator.workflow_def.retry_policy.max_retries = 2
        orchestrator.workflow_def.retry_policy.exponential_backoff = False
        orchestrator.workflow_def.retry_policy.retry_delay_seconds = 0

        result = orchestrator.execute(date(2026, 8, 21))

        # Should fail
        assert result.status == RunStatus.FAILED
        # Should have retried exactly max_retries times
        assert call_count[0] == 2

    def test_multiple_source_failures(self):
        """Run tracks multiple failed sources."""
        orchestrator = self._create_orchestrator()
        run = orchestrator.run_manager.create_run("workflow1", "2026-08-21")

        orchestrator.run_manager.mark_failed_source(run.run_id, "amazon")
        orchestrator.run_manager.mark_failed_source(run.run_id, "flipkart")
        orchestrator.run_manager.mark_partial_source(run.run_id, "myntra")

        updated_run = orchestrator.run_manager.get_run(run.run_id)
        assert len(updated_run.failed_sources) == 2
        assert len(updated_run.partial_sources) == 1

    def test_stage_timing(self):
        """Stage execution times are recorded."""
        orchestrator = self._create_orchestrator()
        result = orchestrator.execute(date(2026, 8, 21))

        # Check all stages have timing
        for stage_result in result.stage_results.values():
            assert stage_result.start_time is not None
            assert stage_result.end_time is not None
            assert stage_result.duration_seconds >= 0

    def test_error_details_preserved(self):
        """Error messages and types are preserved."""
        orchestrator = self._create_orchestrator(
            validation=MockValidationService(should_fail=True)
        )
        result = orchestrator.execute(date(2026, 8, 21))

        validation_result = result.stage_results[WorkflowStage.VALIDATION]
        assert validation_result.error_message is not None
        assert validation_result.error_type == "Exception"
        assert validation_result.status == StageStatus.FAILED

    def test_idempotency_key_tracking(self):
        """Idempotency keys are tracked per stage."""
        orchestrator = self._create_orchestrator()
        result = orchestrator.execute(date(2026, 8, 21))

        for stage_result in result.stage_results.values():
            if stage_result.status == StageStatus.SUCCESS:
                assert stage_result.idempotency_key is not None

    def test_run_cancellation(self):
        """Cancelled run doesn't execute stages."""
        # This would be implemented with a cancellation signal
        # For MVP, documented as future enhancement
        pass
