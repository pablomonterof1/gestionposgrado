
def permisos_usuario(request):
    user = request.user
    permisos = {
        'tiene_permiso_edision': False,
        'tiene_permiso_coordinador': False
    }

    if user.is_authenticated:
        if user.is_superuser:
            permisos['tiene_permiso_edision'] = True
            permisos['tiene_permiso_coordinador'] = True
        elif hasattr(user, 'perfilusuario'):
            rol = user.perfilusuario.rol
            if rol == 4:
                permisos['tiene_permiso_edision'] = True
            elif rol == 3:
                permisos['tiene_permiso_coordinador'] = True

    return permisos