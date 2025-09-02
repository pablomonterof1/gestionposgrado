from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

class ForcePasswordChangeMiddleware:
    """
    Si el usuario tiene como contraseña su propio username,
    lo forzamos a ir a la pantalla de cambio de contraseña.
    Conservamos el destino original en session para no romper 'next'.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo si está autenticado
        if request.user.is_authenticated:
            path = request.path

            # Rutas exentas para evitar bucles
            exempt_names = [
                'password_change',
                'password_change_done',
                'logout',
                'signin',  # por si acaso
                'admin:login',
                'admin:logout',
            ]

            exempt_paths = []
            for name in exempt_names:
                try:
                    exempt_paths.append(reverse(name))
                except NoReverseMatch:
                    pass

            # No interferir con static/media
            if path.startswith('/static/') or path.startswith('/media/'):
                return self.get_response(request)

            # Si la contraseña actual coincide con el username => insegura
            # (Esto no compara texto plano: usa el verificador de Django)
            if request.user.check_password(request.user.username):
                # Si no está ya en una ruta exenta, redirigir a cambio de password
                if not any(path.startswith(p) for p in exempt_paths):
                    # Guardar el destino original una sola vez y solo en GET
                    if request.method == 'GET' and 'post_pwd_change_next' not in request.session:
                        request.session['post_pwd_change_next'] = request.get_full_path()
                    return redirect('password_change')

        return self.get_response(request)