
def permisos_usuario(request):
    user = request.user
    permisos = {
        'tiene_permiso_estudiante': False,
        'tiene_permiso_docente': False,
        'tiene_permiso_coordinador': False,
        'tiene_permiso_edicion': False,
        'tiene_permiso_tutor': False,
        'tiene_permiso_tecnico': False,
        'tiene_permiso_analista': False,
        'tiene_permiso_tecnico_contratos': False,
    }

    if user.is_authenticated:
        # Los superusuarios tienen todos los permisos
        if user.is_superuser:
            for key in permisos.keys():
                permisos[key] = True

        # Usuarios con perfil definido
        elif hasattr(user, 'perfilusuario'):
            rol = user.perfilusuario.rol

            if rol == 1:
                permisos['tiene_permiso_estudiante'] = True
            elif rol == 2:
                permisos['tiene_permiso_docente'] = True
            elif rol == 3:
                permisos['tiene_permiso_coordinador'] = True
            elif rol == 4:
                permisos['tiene_permiso_edicion'] = True
            elif rol == 5:
                permisos['tiene_permiso_tutor'] = True
            elif rol == 6:
                permisos['tiene_permiso_tecnico'] = True
            elif rol == 7:
                permisos['tiene_permiso_analista'] = True
            elif rol == 8:
                permisos['tiene_permiso_tecnico_contratos'] = True

    return permisos
