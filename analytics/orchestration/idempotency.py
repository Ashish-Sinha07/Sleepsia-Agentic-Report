"""Idempotency management for workflow stages."""

import hashlib
import json
from datetime import date
from typing import Dict, Any, Optional


class IdempotencyKeyManager:
    """Generate and manage deterministic idempotency keys."""

    @staticmethod
    def generate_key(stage: str, business_date: date,
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a deterministic idempotency key.

        Uses a hash of stage name, business date, and optional context
        to ensure the same inputs always produce the same key.

        Args:
            stage: Stage name (e.g., "ingestion", "metrics")
            business_date: Business date for the operation
            context: Optional context dict (e.g., platform filters, product SKUs)

        Returns:
            Hex string idempotency key
        """
        key_parts = [stage, str(business_date)]

        if context:
            sorted_context = json.dumps(context, sort_keys=True, default=str)
            key_parts.append(sorted_context)

        combined = "|".join(key_parts)
        hash_obj = hashlib.sha256(combined.encode())
        return hash_obj.hexdigest()[:16]

    @staticmethod
    def generate_ingestion_key(business_date: date,
                               sources: Optional[list] = None) -> str:
        """Generate idempotency key for ingestion stage."""
        context = {"sources": sources} if sources else None
        return IdempotencyKeyManager.generate_key("ingestion", business_date, context)

    @staticmethod
    def generate_validation_key(business_date: date) -> str:
        """Generate idempotency key for validation stage."""
        return IdempotencyKeyManager.generate_key("validation", business_date)

    @staticmethod
    def generate_metrics_key(business_date: date) -> str:
        """Generate idempotency key for metrics stage."""
        return IdempotencyKeyManager.generate_key("metrics", business_date)

    @staticmethod
    def generate_analysis_key(business_date: date) -> str:
        """Generate idempotency key for analysis stage."""
        return IdempotencyKeyManager.generate_key("analysis", business_date)

    @staticmethod
    def generate_insights_key(business_date: date) -> str:
        """Generate idempotency key for insights stage."""
        return IdempotencyKeyManager.generate_key("insights", business_date)

    @staticmethod
    def generate_report_key(business_date: date,
                           report_type: Optional[str] = None) -> str:
        """Generate idempotency key for report stage."""
        context = {"report_type": report_type} if report_type else None
        return IdempotencyKeyManager.generate_key("report", business_date, context)

    @staticmethod
    def generate_distribution_key(business_date: date,
                                 recipients: Optional[list] = None) -> str:
        """Generate idempotency key for distribution stage."""
        context = {"recipients": recipients} if recipients else None
        return IdempotencyKeyManager.generate_key("distribution", business_date, context)

    @staticmethod
    def generate_audit_key(business_date: date, run_id: Optional[str] = None) -> str:
        """Generate idempotency key for audit stage."""
        context = {"run_id": run_id} if run_id else None
        return IdempotencyKeyManager.generate_key("audit", business_date, context)


class IdempotencyCache:
    """In-memory cache for idempotent operation results."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result for idempotency key."""
        return self._cache.get(idempotency_key)

    def set(self, idempotency_key: str, result: Dict[str, Any]):
        """Cache result for idempotency key."""
        self._cache[idempotency_key] = result

    def exists(self, idempotency_key: str) -> bool:
        """Check if result is cached."""
        return idempotency_key in self._cache

    def clear(self):
        """Clear the cache."""
        self._cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)
