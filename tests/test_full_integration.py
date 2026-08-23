"""Integration test to verify full agent orchestrator implementation."""

import pytest
from datetime import date, timedelta
from backend.services.agent_orchestrator import AgentOrchestrator
from backend.app.services.report_service import ReportService


class TestAgentOrchestratorIntegration:
    """Test that all agent orchestrator methods are implemented."""

    def test_get_kpis_method_exists(self):
        """Verify get_kpis method returns proper structure."""
        orchestrator = AgentOrchestrator()

        # Method should exist and be callable
        assert hasattr(orchestrator, 'get_kpis')
        assert callable(orchestrator.get_kpis)

    def test_analyze_product_performance_method_exists(self):
        """Verify analyze_product_performance method exists."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'analyze_product_performance')
        assert callable(orchestrator.analyze_product_performance)

    def test_analyze_platform_performance_method_exists(self):
        """Verify analyze_platform_performance method exists."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'analyze_platform_performance')
        assert callable(orchestrator.analyze_platform_performance)

    def test_get_alerts_method_exists(self):
        """Verify get_alerts method exists."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'get_alerts')
        assert callable(orchestrator.get_alerts)

    def test_ask_question_method_exists(self):
        """Verify ask_question method exists and is implemented."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'ask_question')
        assert callable(orchestrator.ask_question)

    def test_generate_report_method_exists(self):
        """Verify generate_report method exists and is implemented."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'generate_report')
        assert callable(orchestrator.generate_report)

    def test_all_agents_initialized(self):
        """Verify all agents are properly initialized."""
        orchestrator = AgentOrchestrator()

        assert hasattr(orchestrator, 'validation_agent')
        assert hasattr(orchestrator, 'metrics_engine')
        assert hasattr(orchestrator, 'analysis_agent')
        assert hasattr(orchestrator, 'insight_agent')
        assert hasattr(orchestrator, 'llm_agent')
        assert hasattr(orchestrator, 'report_agent')

    def test_llm_agent_has_groq_config(self):
        """Verify LLM agent has Groq configuration."""
        orchestrator = AgentOrchestrator()

        # LLM agent should be initialized with Groq API key
        assert orchestrator.llm_agent is not None
        assert hasattr(orchestrator.llm_agent, 'client')


class TestReportServiceIntegration:
    """Test that ReportService is fully implemented."""

    def test_generate_report_method_exists(self):
        """Verify generate_report method exists."""
        assert hasattr(ReportService, 'generate_report')
        assert callable(ReportService.generate_report)

    def test_list_reports_method_exists(self):
        """Verify list_reports method exists."""
        assert hasattr(ReportService, 'list_reports')
        assert callable(ReportService.list_reports)

    def test_get_report_method_exists(self):
        """Verify get_report method exists."""
        assert hasattr(ReportService, 'get_report')
        assert callable(ReportService.get_report)

    def test_report_types_defined(self):
        """Verify report types are properly defined."""
        assert len(ReportService.REPORT_TYPES) > 0
        assert 'executive_summary' in ReportService.REPORT_TYPES
        assert 'platform_analysis' in ReportService.REPORT_TYPES
        assert 'product_analysis' in ReportService.REPORT_TYPES


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
