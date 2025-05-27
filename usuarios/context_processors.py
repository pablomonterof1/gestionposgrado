

def permiso_edision(request):
    user = request.user
    tiene_permiso = False

    if user.is_authenticated:
        if user.is_superuser:
            tiene_permiso = True
        elif hasattr(user, 'perfilusuario'):
            if user.perfilusuario.rol == 4:
                tiene_permiso = True

    return {
        'tiene_permiso_edision': tiene_permiso
    }