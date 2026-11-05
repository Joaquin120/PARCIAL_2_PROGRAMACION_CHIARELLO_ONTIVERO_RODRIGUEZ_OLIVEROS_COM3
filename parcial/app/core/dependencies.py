from fastapi import HTTPException, Request, status


async def verificar_no_debe_cambiar_password(request: Request) -> None:
    """Dependency verifying that the user is not required to change password.

    Crucial Rule (CONSIGNA_PARCIAL §2.5):
    - Protects the entire protected route group.
    - If user has debe_cambiar_password == True, raises HTTP 403 Forbidden.
    """
    user = getattr(request.state, "user", None)
    if user is not None and getattr(user, "debe_cambiar_password", False) is True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe cambiar su contraseña antes de continuar",
        )
