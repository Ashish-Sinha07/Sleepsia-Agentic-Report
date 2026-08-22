"""Domain models for workflow orchestration."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


class WorkflowStage(str, Enum):
    """Pipeline stages in execution order."""
    INGESTION = "ingestion"
    VALIDATION = "validation"
    METRICS = "metrics"
    ANALYSIS = "analysis"
    INSIGHTS = "insights"
    REPORT = "report"
    DISTRIBUTION = "distribution"
    AUDIT = "audit"


class StageStatus(str, Enum):
    """Status of a single stage execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunStatus(str, Enum):
    """Overall run status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"  # Optional sources failed
    FAILED = "failed"  # Required source failed
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class SourceRequirement(str, Enum):
    """Whether a data source is required or optional."""
    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass
class RetryPolicy:
    """Retry configuration for stages."""
    max_retries: int = 3
    retry_delay_seconds: int = 60
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0

    def get_delay_for_attempt(self, attempt: int) -> int:
        """Get delay in seconds for the given attempt number."""
        if not self.exponential_backoff:
            return self.retry_delay_seconds
        return int(self.retry_delay_seconds * (self.backoff_multiplier ** (attempt - 1)))


@dataclass
class WorkflowDefinition:
    """Declarative workflow pipeline definition."""
    workflow_id: str
    name: str
    stages: List[WorkflowStage] = field(default_factory=lambda: [
        WorkflowStage.INGESTION,
        WorkflowStage.VALIDATION,
        WorkflowStage.METRICS,
        WorkflowStage.ANALYSIS,
        WorkflowStage.INSIGHTS,
        WorkflowStage.REPORT,
        WorkflowStage.DISTRIBUTION,
        WorkflowStage.AUDIT,
    ])
    required_sources: Dict[str, SourceRequirement] = field(default_factory=lambda: {
        "amazon": SourceRequirement.REQUIRED,
        "ads": SourceRequirement.REQUIRED,
        "costs": SourceRequirement.REQUIRED,
    })
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    checkpoint_enabled: bool = True
    idempotency_enabled: bool = True


@dataclass
class StageResult:
    """Result of executing a single stage."""
    stage: WorkflowStage
    status: StageStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    attempt: int = 1
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    warning_messages: List[str] = field(default_factory=list)
    output_data: Dict[str, Any] = field(default_factory=dict)
    idempotency_key: Optional[str] = None

    def set_success(self, output_data: Dict[str, Any] = None):
        """Mark stage as successfully completed."""
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.status = StageStatus.SUCCESS
        if output_data:
            self.output_data = output_data

    def set_warning(self, warning_message: str):
        """Add a warning to the stage result."""
        self.warning_messages.append(warning_message)
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        if self.status != StageStatus.FAILED:
            self.status = StageStatus.WARNING

    def set_failure(self, error_message: str, error_type: str = "Unknown"):
        """Mark stage as failed."""
        self.error_message = error_message
        self.error_type = error_type
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.status = StageStatus.FAILED

    def set_skipped(self):
        """Mark stage as skipped."""
        self.status = StageStatus.SKIPPED
        self.end_time = datetime.utcnow()
        self.duration_seconds = 0


@dataclass
class RunState:
    """Complete state of a workflow run."""
    run_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_id: str = ""
    business_date: str = ""
    status: RunStatus = RunStatus.PENDING
    stage_results: Dict[WorkflowStage, StageResult] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    failed_sources: List[str] = field(default_factory=list)
    partial_sources: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    checkpoints: Dict[WorkflowStage, datetime] = field(default_factory=dict)
    idempotency_keys: Dict[WorkflowStage, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_last_successful_stage(self) -> Optional[WorkflowStage]:
        """Get the last stage that completed successfully."""
        last_successful = None
        for stage in WorkflowStage:
            if stage in self.stage_results:
                if self.stage_results[stage].status == StageStatus.SUCCESS:
                    last_successful = stage
        return last_successful

    def is_complete(self) -> bool:
        """Check if all stages have been executed."""
        return len(self.stage_results) == len(list(WorkflowStage))

    def can_resume_from(self, stage: WorkflowStage) -> bool:
        """Check if we can resume from the given stage."""
        if stage not in self.stage_results:
            return False
        result = self.stage_results[stage]
        return result.status in (StageStatus.SUCCESS, StageStatus.WARNING)

    def mark_partial(self, reason: str):
        """Mark run as partial with reason."""
        self.status = RunStatus.PARTIAL
        self.error_message = reason


@dataclass
class RunResult:
    """Final result of a complete workflow run."""
    run_id: str
    workflow_id: str
    business_date: str
    status: RunStatus
    stage_results: Dict[WorkflowStage, StageResult]
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    failed_sources: List[str]
    partial_sources: List[str]
    error_message: Optional[str]
    report_generated: bool = False
    report_path: Optional[str] = None
    distribution_successful: bool = False
    distribution_error: Optional[str] = None

    @classmethod
    def from_run_state(cls, run_state: RunState) -> "RunResult":
        """Create RunResult from RunState."""
        return cls(
            run_id=run_state.run_id,
            workflow_id=run_state.workflow_id,
            business_date=run_state.business_date,
            status=run_state.status,
            stage_results=run_state.stage_results,
            start_time=run_state.start_time,
            end_time=run_state.end_time,
            duration_seconds=run_state.duration_seconds or 0,
            failed_sources=run_state.failed_sources,
            partial_sources=run_state.partial_sources,
            error_message=run_state.error_message,
        )
