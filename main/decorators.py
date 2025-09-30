from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def role_required(roles):
    """
    Decorador para restringir vistas según el rol del usuario.
    - roles: lista de números de rol permitidos
    Ejemplo:
        @role_required([2])      -> solo docentes
        @role_required([2, 3])   -> docentes y coordinadores
    """
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # El superuser tiene acceso total
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Verificar rol del perfil
            if hasattr(user, "perfilusuario") and user.perfilusuario.rol in roles:
                return view_func(request, *args, **kwargs)

            # Denegar si no cumple
            raise PermissionDenied
        return _wrapped_view
    return decorator