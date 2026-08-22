"""Abstract service interfaces for workflow stages."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Any, Optional


class IngestionService(ABC):
    """Service interface for data ingestion stage."""

    @abstractmethod
    def ingest(self, business_date: date, idempotency_key: str) -> Dict[str, Any]:
        """
        Ingest data from sources for the given business date.

        Args:
            business_date: Date to ingest data for
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with ingestion results and status

        Raises:
            Exception: On critical ingestion failures
        """
        pass


class ValidationService(ABC):
    """Service interface for data validation stage."""

    @abstractmethod
    def validate(self, ingestion_result: Dict[str, Any],
                 idempotency_key: str) -> Dict[str, Any]:
        """
        Validate ingested data.

        Args:
            ingestion_result: Output from ingestion stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with validation results

        Raises:
            Exception: On critical validation failures
        """
        pass


class MetricService(ABC):
    """Service interface for metrics calculation stage."""

    @abstractmethod
    def calculate_metrics(self, validation_result: Dict[str, Any],
                         idempotency_key: str) -> Dict[str, Any]:
        """
        Calculate business metrics from validated data.

        Args:
            validation_result: Output from validation stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with calculated metrics

        Raises:
            Exception: On metric calculation failures
        """
        pass


class AnalysisService(ABC):
    """Service interface for analysis stage."""

    @abstractmethod
    def analyze(self, metrics_result: Dict[str, Any],
               idempotency_key: str) -> Dict[str, Any]:
        """
        Analyze metrics and generate findings.

        Args:
            metrics_result: Output from metrics stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with analysis results

        Raises:
            Exception: On analysis failures
        """
        pass


class InsightService(ABC):
    """Service interface for insights & recommendations stage."""

    @abstractmethod
    def generate_insights(self, analysis_result: Dict[str, Any],
                         idempotency_key: str) -> Dict[str, Any]:
        """
        Generate business insights and recommendations.

        Args:
            analysis_result: Output from analysis stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with insights and recommendations

        Raises:
            Exception: On insight generation failures
        """
        pass


class ReportService(ABC):
    """Service interface for report generation stage."""

    @abstractmethod
    def generate_report(self, insights_result: Dict[str, Any],
                       idempotency_key: str) -> Dict[str, Any]:
        """
        Generate management reports.

        Args:
            insights_result: Output from insights stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with report path and metadata

        Raises:
            Exception: On report generation failures
        """
        pass


class DistributionService(ABC):
    """Service interface for report distribution stage."""

    @abstractmethod
    def distribute(self, report_result: Dict[str, Any],
                  idempotency_key: str) -> Dict[str, Any]:
        """
        Distribute generated reports.

        Args:
            report_result: Output from report stage
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with distribution results

        Raises:
            Exception: On critical distribution failures
        """
        pass


class MonitoringService(ABC):
    """Service interface for audit & monitoring stage."""

    @abstractmethod
    def audit(self, workflow_state: Dict[str, Any],
             idempotency_key: str) -> Dict[str, Any]:
        """
        Perform audit and monitoring of the workflow run.

        Args:
            workflow_state: Complete state from all stages
            idempotency_key: Idempotency key for deduplication

        Returns:
            Dictionary with audit results

        Raises:
            Exception: On critical audit failures
        """
        pass
