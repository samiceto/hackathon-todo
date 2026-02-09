"""Dapr Service Invocation helper for calling other microservices.

This module provides a simple wrapper around Dapr Service Invocation API
to enable service-to-service calls with automatic service discovery,
retries, and mTLS encryption.

Features:
- Service discovery: No need for hardcoded URLs or service IPs
- Retry logic: Automatic retries with exponential backoff
- mTLS: Automatic mutual TLS encryption between services
- Observability: Distributed tracing and metrics via Dapr

Example:
    >>> client = DaprServiceClient()
    >>> result = await client.invoke_service(
    ...     app_id="reminder-service",
    ...     method_name="health",
    ...     http_verb="GET"
    ... )
"""

import logging
from typing import Any, Dict, Optional

from dapr.clients import DaprClient
from dapr.clients.http.client import DaprInvocationHttpClient
from dapr.clients.grpc.client import DaprGrpcClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprServiceClient:
    """Client for invoking other services via Dapr Service Invocation API.

    Provides a simple interface for service-to-service communication using
    Dapr's service invocation building block.

    Attributes:
        use_grpc: Whether to use gRPC protocol (default: False = HTTP)
        dapr_http_port: Dapr HTTP port (default: 3500)
        dapr_grpc_port: Dapr gRPC port (default: 50001)
    """

    def __init__(
        self,
        use_grpc: bool = False,
        dapr_http_port: int = 3500,
        dapr_grpc_port: int = 50001
    ):
        """Initialize DaprServiceClient.

        Args:
            use_grpc: Whether to use gRPC instead of HTTP
            dapr_http_port: Dapr HTTP port
            dapr_grpc_port: Dapr gRPC port
        """
        self.use_grpc = use_grpc
        self.dapr_http_port = dapr_http_port
        self.dapr_grpc_port = dapr_grpc_port

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        http_verb: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Invoke a method on another service via Dapr Service Invocation.

        Args:
            app_id: Dapr app ID of the target service (e.g., "reminder-service")
            method_name: Method/endpoint to call (e.g., "health" or "process-reminders")
            http_verb: HTTP verb (GET, POST, PUT, DELETE, etc.)
            data: Optional request body (will be JSON-serialized)
            metadata: Optional HTTP headers

        Returns:
            Response data from the invoked service

        Raises:
            DaprInternalError: If service invocation fails

        Example:
            >>> client = DaprServiceClient()
            >>> result = await client.invoke_service(
            ...     app_id="reminder-service",
            ...     method_name="health",
            ...     http_verb="GET"
            ... )
            >>> print(result)
            {'status': 'healthy', 'service': 'reminder-service'}
        """
        logger.info(
            f"Invoking service: app_id={app_id}, method={method_name}, "
            f"verb={http_verb}, protocol={'gRPC' if self.use_grpc else 'HTTP'}"
        )

        try:
            if self.use_grpc:
                # Use gRPC protocol
                with DaprGrpcClient(f"localhost:{self.dapr_grpc_port}") as client:
                    response = client.invoke_method(
                        app_id=app_id,
                        method_name=method_name,
                        data=data,
                        http_verb=http_verb,
                        metadata=metadata
                    )
                    return response.json()

            else:
                # Use HTTP protocol
                with DaprClient(http_port=self.dapr_http_port) as client:
                    response = client.invoke_method(
                        app_id=app_id,
                        method_name=method_name,
                        data=data,
                        http_verb=http_verb,
                        metadata=metadata
                    )
                    return response.json()

        except DaprInternalError as e:
            logger.error(
                f"Service invocation failed: app_id={app_id}, method={method_name}, "
                f"error={str(e)}"
            )
            raise

    async def invoke_reminder_service(
        self,
        method_name: str,
        http_verb: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience method to invoke the reminder service.

        Args:
            method_name: Endpoint to call (e.g., "health", "cron")
            http_verb: HTTP verb (GET, POST, etc.)
            data: Optional request body

        Returns:
            Response from reminder service

        Example:
            >>> client = DaprServiceClient()
            >>> result = await client.invoke_reminder_service("health")
            >>> print(result['status'])
            'healthy'
        """
        return await self.invoke_service(
            app_id="reminder-service",
            method_name=method_name,
            http_verb=http_verb,
            data=data
        )

    async def health_check(self, app_id: str) -> bool:
        """Check health of another service via Dapr.

        Args:
            app_id: Dapr app ID of the service to check

        Returns:
            True if service is healthy, False otherwise

        Example:
            >>> client = DaprServiceClient()
            >>> is_healthy = await client.health_check("reminder-service")
            >>> print(is_healthy)
            True
        """
        try:
            result = await self.invoke_service(
                app_id=app_id,
                method_name="health",
                http_verb="GET"
            )
            return result.get("status") == "healthy"

        except Exception as e:
            logger.warning(f"Health check failed for {app_id}: {str(e)}")
            return False


# Singleton instance for dependency injection
_dapr_service_client: Optional[DaprServiceClient] = None


def get_dapr_service_client() -> DaprServiceClient:
    """Get singleton DaprServiceClient instance.

    Returns:
        DaprServiceClient instance
    """
    global _dapr_service_client
    if _dapr_service_client is None:
        _dapr_service_client = DaprServiceClient()
    return _dapr_service_client
