"""Business Analytics module - Metrics Engine and Analysis Agents."""

from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
    TrendMetrics,
    AnalysisResult,
    PerformanceFinding,
)
from analytics.metrics_engine import MetricsEngine
from analytics.analysis_input import AnalysisInput, MetricComparison

__all__ = [
    "ProductMetrics",
    "PlatformMetrics",
    "DailyMetrics",
    "TrendMetrics",
    "AnalysisResult",
    "PerformanceFinding",
    "MetricsEngine",
    "DataAnalysisAgent",
    "AnalysisInput",
    "MetricComparison",
    "LLMAnalysisAgent",
]


def __getattr__(name: str):
    """Load agent exports lazily to avoid a package initialization cycle."""
    if name == "DataAnalysisAgent":
        from agents.analysis_agent import DataAnalysisAgent

        return DataAnalysisAgent
    if name == "LLMAnalysisAgent":
        from agents.llm_analysis_agent import LLMAnalysisAgent

        return LLMAnalysisAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
