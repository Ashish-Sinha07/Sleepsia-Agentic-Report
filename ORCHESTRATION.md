# Phase 7: Workflow Orchestration Engine

**Status**: Implementation Complete

## Overview

The Orchestration Engine is a deterministic workflow controller that executes the complete reporting pipeline in the correct order with:

- Dependency management
- Retry logic with exponential backoff
- Checkpointing for resumability
- Idempotency to prevent duplicate execution
- Failure handling for required and optional sources
- Run tracking and persistence

## Architecture

### Pipeline Stages (in order)

1. **INGESTION** - Load data from sources
2. **VALIDATION** - Validate ingested data
3. **METRICS** - Calculate business metrics
4. **ANALYSIS** - Analyze metrics and generate findings
5. **INSIGHTS** - Generate insights and recommendations
6. **REPORT** - Generate management reports
7. **DISTRIBUTION** - Distribute reports to recipients
8. **AUDIT** - Perform audit and monitoring

### Core Components

#### 1. WorkflowDefinition

Declarative pipeline definition with configuration:

```python
from analytics.orchestration import WorkflowDefinition, RetryPolicy

definition = WorkflowDefinition(
    workflow_id="daily_report",
    name="Daily Business Report",
    required_sources={
        "amazon": SourceRequirement.REQUIRED,
        "ads": SourceRequirement.REQUIRED,
        "costs": SourceRequirement.REQUIRED,
        "flipkart": SourceRequirement.OPTIONAL,
    },
    retry_policy=RetryPolicy(
        max_retries=3,
        retry_delay_seconds=60,
        exponential_backoff=True,
    ),
    checkpoint_enabled=True,
    idempotency_enabled=True,
)
```

#### 2. WorkflowOrchestrator

Main controller that executes the pipeline:

```python
from analytics.orchestration import WorkflowOrchestrator
from datetime import date

orchestrator = WorkflowOrchestrator(
    workflow_definition=definition,
    ingestion_service=ingestion_service,
    validation_service=validation_service,
    metric_service=metric_service,
    analysis_service=analysis_service,
    insight_service=insight_service,
    report_service=report_service,
    distribution_service=distribution_service,
    monitoring_service=monitoring_service,
)

# Execute workflow
result = orchestrator.execute(date(2026, 8, 21))

# Or resume from checkpoint
result = orchestrator.resume(run_id)
```

#### 3. RunManager

Tracks and persists run state:

```python
from analytics.orchestration import RunManager

manager = RunManager(checkpoint_dir="./checkpoints")

# Create run
run = manager.create_run("workflow_id", "2026-08-21")

# Update status
manager.update_run_status(run.run_id, RunStatus.RUNNING)

# Record stage result
manager.record_stage_result(run.run_id, stage_result)

# Complete run
final_result = manager.complete_run(run.run_id)

# Check resumability
if manager.can_resume(run.run_id):
    orchestrator.resume(run.run_id)
```

#### 4. Service Interfaces

All pipeline stages implement abstract service interfaces:

```python
from analytics.orchestration import (
    IngestionService,
    ValidationService,
    MetricService,
    AnalysisService,
    InsightService,
    ReportService,
    DistributionService,
    MonitoringService,
)

class MyIngestionService(IngestionService):
    def ingest(self, business_date: date, idempotency_key: str) -> Dict[str, Any]:
        # Load data from sources
        # Return structured result
        return {"records": 1000, "status": "success"}
```

Services are loosely coupled - the orchestrator depends only on interfaces, not implementations.

#### 5. IdempotencyKeyManager

Generates deterministic idempotency keys:

```python
from analytics.orchestration.idempotency import IdempotencyKeyManager
from datetime import date

# Stage-specific key generators
ingestion_key = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
validation_key = IdempotencyKeyManager.generate_validation_key(date(2026, 8, 21))

# Generic key generator with context
key = IdempotencyKeyManager.generate_key(
    "metrics",
    date(2026, 8, 21),
    {"platform": "amazon", "product": "SLP-1001"}
)

# Same inputs always produce the same key
key1 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
key2 = IdempotencyKeyManager.generate_key("ingestion", date(2026, 8, 21))
assert key1 == key2  # True
```

#### 6. IdempotencyCache

In-memory cache for preventing duplicate operations:

```python
from analytics.orchestration.idempotency import IdempotencyCache

cache = IdempotencyCache()

# Cache result
key = "idempotency_key_123"
result = {"processed": 1000}
cache.set(key, result)

# Check cache
if cache.exists(key):
    cached_result = cache.get(key)
```

## Workflow Execution

### Successful Execution

```
RUN STATE: PENDING
  ↓
Execute INGESTION → SUCCESS
Execute VALIDATION → SUCCESS
Execute METRICS → SUCCESS
Execute ANALYSIS → SUCCESS
Execute INSIGHTS → SUCCESS
Execute REPORT → SUCCESS
Execute DISTRIBUTION → SUCCESS
Execute AUDIT → SUCCESS
  ↓
RUN STATE: SUCCESS
```

### Required Stage Failure

```
RUN STATE: PENDING
  ↓
Execute INGESTION → SUCCESS
Execute VALIDATION → FAILED ← Required source missing
  ↓
SKIP METRICS (dependency failed)
SKIP ANALYSIS (dependency failed)
SKIP INSIGHTS (dependency failed)
SKIP REPORT (dependency failed)
SKIP DISTRIBUTION (dependency failed)
SKIP AUDIT (dependency failed)
  ↓
RUN STATE: FAILED
ERROR: "Required sources failed: amazon"
```

### Optional Stage Failure (Partial Run)

```
RUN STATE: PENDING
  ↓
Execute INGESTION → SUCCESS
Execute VALIDATION → SUCCESS
Execute METRICS → SUCCESS
Execute ANALYSIS → SUCCESS
Execute INSIGHTS → SUCCESS
Execute REPORT → SUCCESS
Execute DISTRIBUTION → WARNING ← Optional service unavailable
  ↓
Continue AUDIT → SUCCESS
  ↓
RUN STATE: PARTIAL
ERROR: "Optional sources unavailable: email_provider"
```

## Retry Logic

Stages are automatically retried on transient failures:

```python
retry_policy = RetryPolicy(
    max_retries=3,
    retry_delay_seconds=60,
    exponential_backoff=True,
    backoff_multiplier=2.0,
)

# Attempt 1: Delay 0s → Fail
# Wait 60 seconds
# Attempt 2: Delay 120s → Fail
# Wait 120 seconds
# Attempt 3: Delay 240s → Fail
# Final failure
```

Retries are only for transient failures. Permanent failures (e.g., data validation error) are not retried indefinitely.

## Checkpointing & Resumability

When a run fails partway through, it can be resumed from the last successful stage:

```python
# First run fails at METRICS stage
result1 = orchestrator.execute(date(2026, 8, 21))
# result1.status == RunStatus.FAILED
# result1.stage_results[WorkflowStage.METRICS].status == StageStatus.FAILED

run_id = result1.run_id

# Fix the issue and resume
# New orchestrator with fixed services
orchestrator2 = WorkflowOrchestrator(...)

# Resume from last successful stage (VALIDATION)
result2 = orchestrator2.resume(run_id)
# Skips INGESTION and VALIDATION
# Retries METRICS and subsequent stages
# result2.status == RunStatus.SUCCESS
```

### Checkpoint Persistence

Run state is persisted to JSON files in the checkpoint directory:

```
./checkpoints/
├── run_id_1.json
├── run_id_2.json
└── run_id_3.json
```

Each checkpoint contains:
- run_id, workflow_id, business_date
- Overall status and timing
- Each stage's result (status, timing, errors)
- Failed and partial sources
- Idempotency keys for each stage

## Idempotency

Idempotency prevents duplicate processing when:

1. Same orchestrator re-runs same workflow
2. Run is resumed from checkpoint
3. Network retry causes duplicate API calls

Idempotency keys are deterministic:

```python
# Same inputs always produce same key
key1 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
key2 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
assert key1 == key2

# Different dates produce different keys
key1 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 21))
key2 = IdempotencyKeyManager.generate_ingestion_key(date(2026, 8, 22))
assert key1 != key2
```

The orchestrator caches results by idempotency key. If a stage is re-executed with the same key, it returns the cached result instead of re-processing.

## Required vs Optional Sources

Configuration determines what happens when sources fail:

```python
definition = WorkflowDefinition(
    required_sources={
        "amazon": SourceRequirement.REQUIRED,  # Failure stops pipeline
        "flipkart": SourceRequirement.OPTIONAL,  # Failure continues as partial
    },
)
```

- **REQUIRED**: Failure marks entire run as FAILED, stops dependent stages
- **OPTIONAL**: Failure marks run as PARTIAL, continues to completion

## Run State & Results

### RunState

Current state of an in-progress run:

```python
run = RunState(
    run_id="abc123",
    workflow_id="daily_report",
    business_date="2026-08-21",
    status=RunStatus.RUNNING,
    stage_results={
        WorkflowStage.INGESTION: StageResult(...),
        WorkflowStage.VALIDATION: StageResult(...),
    },
    failed_sources=["amazon"],
    partial_sources=["flipkart"],
    checkpoints={
        WorkflowStage.INGESTION: datetime(...),
    },
)
```

### StageResult

Result of executing a single stage:

```python
result = StageResult(
    stage=WorkflowStage.INGESTION,
    status=StageStatus.SUCCESS,
    start_time=datetime(...),
    end_time=datetime(...),
    duration_seconds=12.5,
    attempt=1,
    output_data={"records": 1000},
    idempotency_key="key123",
)
```

### RunResult

Final result of complete execution:

```python
result = RunResult(
    run_id="abc123",
    workflow_id="daily_report",
    business_date="2026-08-21",
    status=RunStatus.SUCCESS,
    duration_seconds=45.2,
    stage_results={...},
    failed_sources=[],
    partial_sources=[],
    report_generated=True,
    report_path="/reports/report_2026_08_21.pdf",
)
```

## Error Handling

### Stage Errors

All exceptions are caught and recorded:

```python
result = orchestrator.execute(date(2026, 8, 21))

for stage, stage_result in result.stage_results.items():
    if stage_result.status == StageStatus.FAILED:
        print(f"{stage.value} failed:")
        print(f"  Error: {stage_result.error_message}")
        print(f"  Type: {stage_result.error_type}")
        print(f"  Attempts: {stage_result.attempt}")
```

### Critical Failures

Fatal errors are recorded and prevent dependent stages:

```python
if result.status == RunStatus.FAILED:
    print(f"Workflow failed: {result.error_message}")
    
    # Analyze which sources failed
    if result.failed_sources:
        print(f"Failed required sources: {result.failed_sources}")
    if result.partial_sources:
        print(f"Unavailable optional sources: {result.partial_sources}")
```

## Integration with Existing Services

The orchestrator integrates with existing analytics services:

```
WorkflowOrchestrator
  ├─ Ingestion Service
    ├─ Validation Service (agents/validation_agent.py)
  ├─ Metric Service (analytics/metrics_engine.py)
    ├─ Analysis Service (agents/analysis_agent.py)
    ├─ Insight Service (agents/insight_recommendation_agent.py)
  ├─ Report Service (analytics/report_builder.py)
  ├─ Distribution Service (analytics/distribution_service.py)
  └─ Monitoring Service (custom audit/logging)
```

Each service implements the corresponding interface.

## Testing

Comprehensive test suite covers:

- Idempotency key generation
- Idempotency cache operations
- Run manager lifecycle
- Checkpoint persistence and recovery
- Successful complete workflow execution
- Stage execution order
- Required stage failure handling
- Optional stage failure handling
- Retry logic with transient failures
- Permanent failure after retries
- Run resumability
- State tracking and timing
- Error preservation
- Multiple source failures

Run tests:

```bash
python -m pytest tests/test_orchestration.py -v
```

## Usage Example

Complete end-to-end usage:

```python
from analytics.orchestration import WorkflowOrchestrator, WorkflowDefinition
from datetime import date

# Create services (implement interfaces)
ingestion = MyIngestionService()
validation = MyValidationService()
metrics = MyMetricService()
analysis = MyAnalysisService()
insights = MyInsightService()
reports = MyReportService()
distribution = MyDistributionService()
monitoring = MyMonitoringService()

# Create workflow definition
definition = WorkflowDefinition(
    workflow_id="daily_report",
    name="Daily Business Report",
)

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    workflow_definition=definition,
    ingestion_service=ingestion,
    validation_service=validation,
    metric_service=metrics,
    analysis_service=analysis,
    insight_service=insights,
    report_service=reports,
    distribution_service=distribution,
    monitoring_service=monitoring,
)

# Execute workflow
result = orchestrator.execute(date(2026, 8, 21))

# Check result
if result.status == RunStatus.SUCCESS:
    print("✅ Workflow completed successfully")
    print(f"Report: {result.report_path}")
elif result.status == RunStatus.PARTIAL:
    print("⚠️  Workflow completed with missing optional sources")
    print(f"Missing: {result.partial_sources}")
    print(f"Report: {result.report_path}")
else:
    print("❌ Workflow failed")
    print(f"Error: {result.error_message}")
    print(f"Failed sources: {result.failed_sources}")
    
    # Can resume if desired
    if orchestrator.run_manager.can_resume(result.run_id):
        # Fix issue and retry
        result2 = orchestrator.resume(result.run_id)
```

## Architecture Constraints

1. **Deterministic orchestration**: No LLM-based decisions, pure logic
2. **Interface-based design**: Services are loosely coupled via interfaces
3. **Idempotent operations**: Same inputs always produce same output
4. **Checkpoint recovery**: Can resume from last successful stage
5. **Clear error handling**: Distinguishes required vs optional failures
6. **Explicit dependencies**: Stages execute in fixed order, no dynamic ordering
7. **No service discovery**: Services provided at instantiation time
8. **JSON checkpoint format**: Human-readable, versionable state

## Future Enhancements

- Workflow cancellation signal
- Parallel stage execution (currently sequential)
- Dynamic stage routing based on data
- Distributed orchestration (multiple machines)
- Metrics and monitoring integration
- Scheduled workflow execution
- Workflow versioning and rollback
