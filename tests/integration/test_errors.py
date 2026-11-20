def test_error_contains_correlation_id(client):

    response = client.get(
        "/customers/999"
    )

    body = response.json()

    assert response.status_code == 404

    assert "correlation_id" in body

def test_supplied_correlation_id_is_propagated(client):

    correlation_id = "integration-test-123"

    response = client.get(
        "/customers/999",
        headers={
            "X-Correlation-ID": correlation_id
        },
    )

    assert (
        response.json()["correlation_id"] == correlation_id
    )

    assert (
        response.headers["X-Correlation-ID"] == correlation_id
    )

def test_missing_customer_returns_safe_error(client):

    response = client.get(
        "/customers/999"
    )

    assert response.status_code == 404

    body = response.json()

    assert body["code"] == "CUSTOMER_NOT_FOUND"
    assert "correlation_id" in body

    assert "traceback" not in str(body).lower()
    assert "sql" not in str(body).lower()

from fastapi.testclient import TestClient
from src.api.main import app
from src.dependencies import get_complaint_service

class BrokenComplaintService:

    def get_customer(self, customer_id):
        raise RuntimeError(
            "INTERNAL DATABASE INFORMATION - DON'T LEAK"
        )
    
    def test_unexpected_error_returns_safe_500():

        def broken_service():
            return BrokenComplaintService()
        
        app.dependency_overrides[
            get_complaint_service
        ] = broken_service

        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as client:

            response = client.get(
                "/customers/1"
            )
        
        app.dependency_overrides.clear()

        assert response.status_code == 500

        body = response.json()

        assert body["code"] == "INTERNAL ERROR"

        assert body["message"] == (
            "Unexpected error. Quote the correlation ID"
            "when reporting it."
        )

        assert "correlation_id" in body

        assert (
            "INTERNAL DATABASE INFORMATION - DON'T LEAK"
            not in str(body)
        )

from src.domain.errors import DependencyUnavailable

def test_unavailable_dependency_returns_503():

    def unavailable_service():
        raise DependencyUnavailable(
            "Database unavailable."
        )
    
    app.dependency_overrides[
        get_complaint_service
    ] = unavailable_service

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as client:

            response = client.get(
                "/customers/1"
            )
        
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503

    body = response.json()

    assert body["code"] == "DEPENDENCY_UNAVAILABLE"
    assert "correlation_id" in body