from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from parcial.app.main import app, lifespan


@pytest.mark.asyncio
async def test_lifespan_initializes_state_and_disposes() -> None:
    """Verifies that lifespan sets up fictitious password hash, engine, and cleans up."""
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("parcial.app.main.engine", mock_engine):
        async with lifespan(app):
            assert hasattr(app.state, "fictitious_password_hash")
            assert app.state.fictitious_password_hash.startswith("$2b$")
            assert hasattr(app.state, "engine")
            assert hasattr(app.state, "sessionmaker")
            mock_engine.dispose.assert_not_called()

        mock_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_open_route_group_health_live() -> None:
    """Verifies that open route group handles /health/live with 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_protected_route_group_allows_normal_user() -> None:
    """Verifies protected route group allows access when debe_cambiar_password is False."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected/ping")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_protected_route_group_blocks_when_must_change_password() -> None:
    """Verifies protected route group returns 403 Forbidden when debe_cambiar_password is True."""
    from fastapi import Request

    async def mock_user_middleware(request: Request, call_next):
        request.state.user = SimpleNamespace(debe_cambiar_password=True)
        return await call_next(request)

    app.middleware_stack = None  # Reset stack to add middleware dynamically for test
    app.middleware("http")(mock_user_middleware)
    app.build_middleware_stack()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected/ping")
        assert response.status_code == 403
        assert "Debe cambiar su contraseña" in response.json()["detail"]
