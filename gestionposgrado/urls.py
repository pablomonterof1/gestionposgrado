"""
URL configuration for gestionposgrado project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from usuarios import views as user_views
from programaacademico import views as programaacademico_views
from programasposgrado import views as programasposgrado_views
from cuerpoacademico import views as cuerpoacademico_views
from postulacion import views as postulacion_views
from rae import views as rae_views
from django.conf.urls.static import static
from django.conf import settings
from datosposgrado import views as datosposgrado_views
from seleccionperfiles import views as seleccionperfiles_views
from aulavirtual import views as aulavirtual_views
from django.conf.urls.static import static
from django.conf import settings
from datosposgrado import views as datosposgrado_views
from administracionposgrado import views as administracionposgrado_views
from perfeccionamientodocente import views as perfeccionamientodocente_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    path('periodosacademicosmain/', main_views.periodosacademicosmain, name='periodosacademicosmain'),
    path('programasdemaestria/<int:periodo_id>/', main_views.programasdemaestria, name='programasdemaestria'),
    path('programamaestria/<int:programa_id>/', main_views.ProgramaMaestria, name='programamaestria'),
    
    #Gestion de usuarios
    path('signup/', user_views.signup, name='signup'),
    path('perfil/', user_views.perfil, name='perfil'),
    path('perfil/editar/', user_views.perfil_editar, name='perfil_editar'),
    path('usuariodp/<int:user_id>/editar/', user_views.usuario_editar_dp, name='usuario_editar_dp'),
    path('perfil/password/', user_views.perfil_password, name='perfil_password'),
    path('logout/', user_views.signout, name='logout'),
    path('signin/', user_views.signin, name='signin'),
    path('gestionusuarios/', user_views.datosUsuario, name='gestionusuarios'),
    path('actualizar-rol/<int:usuario_id>/', user_views.actualizar_rol_usuario, name='actualizar_rol_usuario'),
    path('docentedp/create/<int:periodo_id>', user_views.docentedp_create, name='docentedp_create'),
    path('tutordp/create/<int:periodo_id>', user_views.tutordp_create, name='tutordp_create'),
    path('estudiantedp/create/<int:periodo_id>', user_views.estudiantedp_create, name='estudiantedp_create'),
    path('coordinadordp/create/<int:periodo_id>', user_views.coordinadordp_create, name='coordinadordp_create'),
    path('password/change/', user_views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', user_views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('usuarioscompletos/', user_views.CrearUsuarioCompleto, name='usuarioscompletos'),
    path('usuarios/<int:user_id>/editar/', user_views.usuario_editar, name='usuario_editar'),


    path('docentepm/create/<int:programa_id>', user_views.docentepm_create, name='docentepm_create'),
    path('estudiantepm/create/<int:programa_id>', user_views.estudiantepm_create, name='estudiantepm_create'),


    #Gestion de programas de posgrado
    path('maestrias/', programasposgrado_views.maestrias, name='maestrias'),
    path('maestrias/create/', programasposgrado_views.maestrias_create, name='maestrias_create'),
    path('maestrias/<int:maestria_id>/', programasposgrado_views.maestrias_detail, name='maestrias_detail'),
    path('maestrias/<int:maestria_id>/delete', programasposgrado_views.maestrias_delete, name='maestrias_delete'),
    path('modulos/<int:maestria_id>', programasposgrado_views.modulos, name='modulos'),
    path('modulos/create/<int:maestria_id>', programasposgrado_views.modulos_create, name='modulos_create'),
    path('modulos/<int:modulo_id>/', programasposgrado_views.modulos_update, name='modulos_update'),
    path('modulos/<int:modulo_id>/delete', programasposgrado_views.modulos_delete, name='modulos_delete'),
    path('periodosacademicos/', programasposgrado_views.periodosacademicos, name='periodosacademicos'),
    path('modalidad/', programasposgrado_views.modalidad, name='modalidad'),
    path('modalidadtitulacion/', programasposgrado_views.modalidadtitulacion, name='modalidadtitulacion'),
    path('perfilingreso/', programasposgrado_views.perfildeingreso, name='perfilingreso'),
    path('programasdeposgrado/', programasposgrado_views.programasdeposgrado, name='programasdeposgrado'),
    path('programadeposgrado/select/', programasposgrado_views.programadeposgrado_select, name='programadeposgrado_select'),
    path('programadeposgrado/create/', programasposgrado_views.programadeposgrado_create, name='programadeposgrado_create'),
    path('programadeposgrado/<int:programadeposgrado_id>/delete', programasposgrado_views.programadeposgrado_delete, name='programadeposgrado_delete'),
    path('programadeposgrado/<int:programadeposgrado_id>', programasposgrado_views.programadeposgrado_update, name='programadeposgrado_update'),
    path('campoamplio/', programasposgrado_views.campoamplio, name='campoamplio'),

    #Información del programa de posgrado
    path('informacionprogramaposgrado/<int:programa_id>/', administracionposgrado_views.informacionprogramaposgrado, name='informacionprogramaposgrado'),
    path('valorprogramaposgrado/<int:programa_id>/', administracionposgrado_views.valorprogramaposgrado_detail, name='valorprogramaposgrado_detail'),
    path('valorprogramaposgrado/create/<int:programa_id>', administracionposgrado_views.valorprogramaposgrado_create, name='valorprogramaposgrado_create'),
    path('valorprogramaposgrado/<int:programa_id>/update', administracionposgrado_views.valorprogramaposgrado_update, name='valorprogramaposgrado_update'),
    path('programa/<int:programa_id>/contratos/', administracionposgrado_views.contratos_coordinadores_programa, name='contratos_coordinadores_programa'),
    path('programa/<int:programa_id>/coordinador/<int:coordinador_id>/periodo/nuevo/', administracionposgrado_views.coordinadorperiodo_create, name='coordinadorperiodo_create'),
    path('programa/<int:programa_id>/coordinador/<int:coordinador_id>/periodo/<int:pk>/editar/', administracionposgrado_views.coordinadorperiodo_update, name='coordinadorperiodo_update'),
    path('programa/<int:programa_id>/coordinador/<int:coordinador_id>/periodo/<int:pk>/eliminar/', administracionposgrado_views.coordinadorperiodo_delete, name='coordinadorperiodo_delete'),

    path('programa/<int:programa_id>/pagos/coordinadores/', administracionposgrado_views.pagos_coordinadores_programa, name='pagos_coordinadores_programa'),
    path('programa/<int:programa_id>/pagos/contrato/<int:contrato_id>/nuevo/', administracionposgrado_views.coordinadorpago_create_by_contrato, name='coordinadorpago_create_by_contrato'),
    path('programa/<int:programa_id>/pagos/<int:pago_id>/editar/', administracionposgrado_views.coordinadorpago_update, name='coordinadorpago_update'),
    path('programa/<int:programa_id>/pagos/<int:pago_id>/eliminar/', administracionposgrado_views.coordinadorpago_delete, name='coordinadorpago_delete'),

    path('programa/<int:programa_id>/docentes/contratos/', administracionposgrado_views.docentes_contratos_programa, name='docentes_contratos_programa'),
    path('programa/<int:programa_id>/docentes/contrato/<int:contrato_id>/gestion/nuevo/', administracionposgrado_views.contratodocente_gestion_create, name='contratodocente_gestion_create'),
    path('programa/<int:programa_id>/docentes/contrato/<int:contrato_id>/gestion/editar/', administracionposgrado_views.contratodocente_gestion_update, name='contratodocente_gestion_update'),

    path('programa/<int:programa_id>/tutores/contratos/', administracionposgrado_views.tutores_contratos_programa, name='tutores_contratos_programa'),
    path('programa/<int:programa_id>/tutores/contrato/<int:contrato_id>/gestion/nuevo/', administracionposgrado_views.contratotutor_gestion_create, name='contratotutor_gestion_create'),
    path('programa/<int:programa_id>/tutores/contrato/<int:contrato_id>/gestion/editar/', administracionposgrado_views.contratotutor_gestion_update, name='contratotutor_gestion_update'),

    path('programa/<int:programa_id>/estudiantes/', administracionposgrado_views.estudiantes_programa_list, name='estudiantes_programa_list'),
    path('programa/<int:programa_id>/estudiantes/<int:user_id>/editar/', administracionposgrado_views.estudiante_programa_gestion_upsert, name='estudiante_programa_gestion_upsert'),

    path("programa/<int:programa_id>/reporte.pdf", administracionposgrado_views.programa_reporte_pdf,  name="programa_reporte_pdf"),

    path('programa/<int:programa_id>/pao/', administracionposgrado_views.programa_pao_configurar, name='programa_pao_configurar'),


    #Especialidades Medicas
    path('especialidadesmedicas/', programasposgrado_views.especialidadesmedicas, name='especialidadesmedicas'),
    path('especialidadesmedicas/create', programasposgrado_views.especialidadesmedicas_create, name='especialidadesmedicas_create'),
    path('especialidadesmedicas/<int:especialidadesmedicas_id>/', programasposgrado_views.especialidadesmedicas_detail, name='especialidadesmedicas_detail'),
    path('especialidadesmedicas/<int:especialidadesmedicas_id>/delete', programasposgrado_views.especialidadesmedicas_delete, name='especialidadesmedicas_delete'),
    path('modulosem/<int:especialidadesmedicas_id>', programasposgrado_views.modulosem, name='modulosem'),
    path('modulosem/create/<int:especialidadesmedicas_id>', programasposgrado_views.modulosem_create, name='modulosem_create'),
    path('modulosem/<int:moduloem_id>/', programasposgrado_views.modulosem_update, name='modulosem_update'),
    path('modulosem/<int:moduloem_id>/delete', programasposgrado_views.modulosem_delete, name='modulosem_delete'),
    path('programasdeespecialidadesmedicas/', programasposgrado_views.programasdeespecialidadesmedicas, name='programasdeespecialidadesmedicas'),
    path('programasdeespecialidadesmedicas/select/', programasposgrado_views.programasdeespecialidadesmedicas_select, name='programasdeespecialidadesmedicas_select'),
    path('programasdeespecialidadesmedicas/create/', programasposgrado_views.programasdeespecialidadesmedicas_create, name='programasdeespecialidadesmedicas_create'),
    path('programasdeespecialidadesmedicas/<int:programadeespecialidadesmedicas_id>', programasposgrado_views.programasdeespecialidadesmedicas_update, name='programasdeespecialidadesmedicas_update'),
    path('programasdeespecialidadesmedicas/<int:programadeespecialidadesmedicas_id>/delete', programasposgrado_views.programasdeespecialidadesmedicas_delete, name='programasdeespecialidadesmedicas_delete'),
   

    #Programa academico
    #Admision
    path('admision/<int:programa_id>/', programaacademico_views.admision, name='admision'),
    path('admision/create/<int:programa_id>', programaacademico_views.admision_create, name='admision_create'),
    path('admisiondetail/<int:admision_id>/', programaacademico_views.admision_detail, name='admision_detail'),
    path('admisiondelete/<int:admision_id>/', programaacademico_views.admision_delete, name='admision_delete'),
    #Diseno curricular
    path('disenocurricular/<int:programa_id>/', programaacademico_views.disenocurricular, name='disenocurricular'),
    path('disenocurricular/create/<int:programa_id>', programaacademico_views.disenocurricular_create, name='disenocurricular_create'),
    path('disenocurriculardetail/<int:disenocurricular_id>/', programaacademico_views.disenocurricular_detail, name='disenocurricular_detail'),
    path('disenocurriculardelete/<int:disenocurricular_id>/', programaacademico_views.disenocurricular_delete, name='disenocurricular_delete'),
    #Titulacion
    path('titulacion/<int:programa_id>/', programaacademico_views.titulacion, name='titulacion'),
    path('titulacion/create/<int:programa_id>', programaacademico_views.titulacion_create, name='titulacion_create'),
    path('titulaciondetail/<int:titulacion_id>/', programaacademico_views.titulacion_detail, name='titulacion_detail'),
    path('titulaciondelete/<int:titulacion_id>/', programaacademico_views.titulacion_delete, name='titulacion_delete'),


    #Cuerpo academico
    #Composición
    path('composicionca/<int:programa_id>/', cuerpoacademico_views.composicion, name='composicionca'),


    #RAE
    #Reactivos
    path('reactivosprograma/<int:programa_id>/', rae_views.reactivosprograma, name='reactivosprograma'),
    path('reactivosmodulo/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosmodulo, name='reactivosmodulo'),
    path('reactivosmc/create/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosmc_create, name='reactivosmc_create'),
    path('reactivosmc/<int:reactivo_id>/', rae_views.reactivosmc_update, name='reactivosmc_update'),
    path('reactivosmc/<int:reactivo_id>/delete', rae_views.reactivosmc_delete, name='reactivosmc_delete'),
    path('reactivosmodulodocente/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosmodulodocente, name='reactivosmodulodocente'),
    path('reactivosmc/create/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosmc_create, name='reactivosmc_create'),
    path('reactivosdocente/create/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosdocente_create, name='reactivosdocente_create'),
    path('reactivosmc/<int:reactivo_id>/', rae_views.reactivosmc_update, name='reactivosmc_update'),
    path('reactivosdocente/<int:reactivo_id>/', rae_views.reactivosdocente_update, name='reactivosdocente_update'),
    path('reactivosmc/<int:reactivo_id>/delete', rae_views.reactivosmc_delete, name='reactivosmc_delete'),
    path('reactivosdocente/<int:reactivo_id>/delete', rae_views.reactivosdocente_delete, name='reactivosdocente_delete'),
    path('reactivosmcvalidate/<int:reactivo_id>/', rae_views.reactivosmc_validate, name='reactivosmc_validate'),
    path('reactivosprogramaposgrado/<int:programa_id>/', rae_views.reactivos_programaposgrado, name='reactivos_programaposgrado'),
    path('raeprogramaposgrado/<int:programa_id>/', rae_views.rae_programaposgrado, name='rae_programaposgrado'),
    path('reactivosmodulorae/create/<int:programa_id>/<int:modulo_id>/', rae_views.reactivosmodulorae_create, name='reactivosmodulorae_create'),
    path('programa/<int:programa_id>/evaluaciones/', rae_views.evaluacionrae_programaposgrado, name='evaluacionrae_programaposgrado'),
    path('evaluacionrae_activar/<int:programa_id>/<str:tipo>/', rae_views.evaluacionrae_activar, name='evaluacionrae_activar' ),
    path('evaluacionrae_update/<int:evaluacion_id>/', rae_views.evaluacionrae_update, name='evaluacionrae_update' ),
    path('evaluaciones/disponibles/<int:programa_id>/', rae_views.evaluacionesrae_disponibles, name='evaluacionesrae_disponibles'),
    path('evaluacion/rendir/<int:evaluacion_id>/', rae_views.evaluacionrae_rendir, name='evaluacionrae_rendir'),
    path('evaluacion/guardar_parcial/<int:evaluacion_id>/', rae_views.guardar_parcial_rae, name='guardar_parcial_rae'),
    path('evaluacion/<int:evaluacion_id>/resultado/', rae_views.resultadorae_estudiante, name='resultadorae_estudiante'),
    path('evaluacion/<int:programa_id>/<int:evaluacion_id>/resultados/', rae_views.resultadosrae_programa, name='resultadosrae_programa'),
    path('evaluacion/<int:evaluacion_id>/estudiante/<int:estudiante_id>/', rae_views.detalle_resultado_estudiante, name='detalle_resultado_estudiante'),
    path('evaluacion/<int:evaluacion_id>/estudiante/<int:estudiante_id>/borrar/', rae_views.detalle_resultado_estudiante_borrar, name='detalle_resultado_estudiante_borrar'),
    path('evaluacion/<int:evaluacion_id>/resultado/pdf/', rae_views.resultado_estudiante_pdf, name='resultado_estudiante_pdf'),
    path('evaluacion/<int:evaluacion_id>/eliminar/', rae_views.evaluacionrae_eliminar, name='evaluacionrae_eliminar'),
    path('reactivos_por_evaluacion/<int:evaluacion_id>/', rae_views.reactivos_por_evaluacion,name='reactivos_por_evaluacion' ),
    path('exportar_resultados_excel/<int:programa_id>/<int:evaluacion_id>/', rae_views.exportar_resultados_excel, name='exportar_resultados_excel'),
    path('programa/<int:programa_id>/estructura-rae/', rae_views.estructura_rae_programa, name='estructura_rae_programa'),
    path('programa/<int:programa_id>/componente/crear/', rae_views.componente_rae_create, name='componente_rae_create'),
    path('componente/<int:componente_id>/editar/', rae_views.componente_rae_update, name='componente_rae_update'),
    path('componente/<int:componente_id>/eliminar/', rae_views.componente_rae_delete, name='componente_rae_delete'),
    path('subcomponente/<int:subcomponente_id>/modulos/', rae_views.subcomponente_asignar_modulos, name='subcomponente_asignar_modulos'),
    path('subcomponente/<int:subcomponente_id>/eliminar/', rae_views.subcomponente_rae_delete, name='subcomponente_rae_delete'),
    path('rae/<int:programa_id>/importar-reactivos-por-modulo/', rae_views.importar_reactivos_rae_por_modulo, name='importar_reactivos_rae_por_modulo'),
    path('reactivos/<int:programa_id>/<int:modulo_id>/quitar-compartido/<int:reactivo_id>/', rae_views.quitar_compartido_reactivo, name='quitar_compartido_reactivo'),
    path('reactivos/<int:programa_id>/<int:modulo_id>/quitar-compartidos/', rae_views.quitar_compartidos_modulo, name='quitar_compartidos_modulo'),


    #DATOSPOSGRADO
    path('periodosacademicosdp/', datosposgrado_views.periodosacademicosdp, name='periodosacademicosdp'),
    path('datosposgrado/<int:periodo_id>/', datosposgrado_views.datosposgrado, name='datosposgrado'),
    #Contratos docentes
    path('contratosdocentes/<int:periodo_id>/', datosposgrado_views.contratosdocentes, name='contratosdocentes'),
    path('contratosdocentes/create/<int:periodo_id>', datosposgrado_views.contratosdocentes_create, name='contratosdocentes_create'),
    path('contratosdocentesupdate/<int:contratosdocentes_id>/<int:periodo_id>', datosposgrado_views.contratosdocentes_update, name='contratosdocentes_update'),
    path('contratosdocentes/<int:contratosdocentes_id>/<int:periodo_id>/delete', datosposgrado_views.contratosdocentes_delete, name='contratosdocentes_delete'),
    # path('api/modulos/<int:programa_id>/', datosposgrado_views.obtener_modulos_por_maestria, name='obtener_modulos_por_maestria'),
    path('api/modulos/<str:tipo>/<int:programa_id>/', datosposgrado_views.obtener_modulos_por_programa, name='obtener_modulos_por_programa'),
    #Contratos tutores
    path('contratotutor/<int:periodo_id>/', datosposgrado_views.contratotutor, name='contratotutor'),
    path('contratotutor/create/<int:periodo_id>', datosposgrado_views.contratotutor_create, name='contratotutor_create'),
    path('contratotutorupdate/<int:contratotutor_id>/<int:periodo_id>', datosposgrado_views.contratotutor_update, name='contratotutor_update'),
    path('contratotutor/<int:contratotutor_id>/<int:periodo_id>/delete', datosposgrado_views.contratotutor_delete, name='contratotutor_delete'),
    #Contratos coordinadores
    path('contratocoordinador/<int:periodo_id>/', datosposgrado_views.contratocoordinador, name='contratocoordinador'),
    path('contratocoordinador/create/<int:periodo_id>', datosposgrado_views.contratocoordinador_create, name='contratocoordinador_create'),
    path('contratocoordinadorupdate/<int:contratocoordinador_id>/<int:periodo_id>', datosposgrado_views.contratocoordinador_update, name='contratocoordinador_update'),
    path('contratocoordinador/<int:contratocoordinador_id>/<int:periodo_id>/delete', datosposgrado_views.contratocoordinador_delete, name='contratocoordinador_delete'),
    #Reportes
    path('dashboard/contrataciones/', datosposgrado_views.dashboard_contrataciones_general, name='dashboard_contrataciones_general'),
    path('dashboard/contrataciones/persona/<int:user_id>/', datosposgrado_views.detalle_contrataciones_persona, name='detalle_contrataciones_persona'),
    #Seleccion de perfiles
    path('seleccionp/<int:periodo_id>/<int:modulo_id>/', seleccionperfiles_views.seleccionp, name='seleccionp'),
    path('periodosacademicosp/', seleccionperfiles_views.periodosacademicosp, name='periodosacademicosp'),    
    path('datosposgradosp/<int:periodo_id>/', seleccionperfiles_views.datosposgradosp, name='datosposgradosp'),
    path('datosmodulossp/<int:programa_id>/', seleccionperfiles_views.datosmodulossp, name='datosmodulossp'),
    path('ternapmmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.ternamodulopmsp, name='ternapmmsp'),
    path('crearternamodulopmmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.crearternamodulopmmsp, name='crearternamodulopmmsp'),
    path('docentesdpmmsp/create/<int:programa_id>/<int:modulo_id>/', user_views.docentepmmsp_create, name='docentesdpmmsp'),
    path('modificarternamodulopmmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.modificarternamodulopmmsp, name='modificarternamodulopmmsp'),
    path('responsablep/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.responsablep, name='responsablep'),
    path('responsablepcoordinador/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.responsablepcoordinador, name='responsablepcoordinador'),
    path('asignar_responsable/<int:responsable_id>/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.asignar_responsable, name='asignar_responsable'),
    path('ternamodulocoordinadorpmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.ternamodulocoordinadorpmsp, name='ternamodulocoordinadorpmsp'),
    path('crearternamodulocoordinadorpmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.crearternamodulocoordinadorpmsp, name='crearternamodulocoordinadorpmsp'),
    path('modificarternamodulocoordinadorpmsp/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.modificarternamodulocoordinadorpmsp, name='modificarternamodulocoordinadorpmsp'),
    path('asignar_responsable_coordinador/<int:responsable_id>/<int:programa_id>/<int:modulo_id>/', seleccionperfiles_views.asignar_responsable_coordinador, name='asignar_responsable_coordinador'),
    path('coordinadorpmmsp_create/<int:programa_id>/<int:modulo_id>/', user_views.coordinadorpmmsp_create, name='coordinadorpmmsp_create'),
    #POSTULACION
    #UsuarioPostulacionEspecialidadesMédicas 



    #POSTULACION
    #UsuarioPostulacionEspecialidadesMédicas

    path('especialidadesmedicaspos/', postulacion_views.especialidadesmedicaspos, name='especialidadesmedicaspos'),
    path('usuariopostulacion/<int:em_id>/', postulacion_views.usuarriops_create, name='usuariopostulacion'),
    path('informacionps/upload/<int:em_id>/', postulacion_views.informacionps_upload, name='informacionps_upload'),
    path('documentospsenviados/', postulacion_views.documentosps_enviados, name='documentospsenviados'),
    path('documentospsvalidados/<int:em_id>/', postulacion_views.documentosps_validados, name='documentospsvalidados'),
    path('documentospsporvalidar/<int:em_id>/', postulacion_views.documentosps_porvalidar, name='documentospsporvalidar'),
    path('documentospsvalidar/<int:doc_id>/<int:em_id>/', postulacion_views.documentosps_validar, name='documentospsvalidar'),
    path('documentospsnovalidar/', postulacion_views.documentosps_novalidar, name='documentospsnovalidar'),


    #USUARIOSMATRICULADOS
    path('usuariosmatriculadosprogramam/<int:programa_id>/', user_views.UsuariosMatriculadosProgramaM, name='usuariosmatriculadosprogramam'),
    path('usuariosmatricularprogramam/<int:programa_id>/', user_views.UsuariosMatricularProgramaM, name='usuariosmatricularprogramam'),
    path('borarusuariosmatriculadosprogramam/<int:programa_id>/<int:usuario_id>/', user_views.BorrarUsuariosMatricularProgramaM, name='borarusuariosmatriculadosprogramam'),
    #DOCENTESMATRICULADOS
    path('docentesmatriculadosmodulom/<int:programa_id>/', user_views.DocentesMatriculadosModuloM, name='docentesmatriculadosmodulom'),
    path('docentesmatricularmodulom/<int:programa_id>/', user_views.DocentesMatricularModuloM, name='docentesmatricularmodulom'),
    path('borardocentesmatriculadosmodulom/<int:programa_id>/<int:docente_id>/<int:modulo_id>/', user_views.BorrarDocentesMatricularModuloM, name='borardocentesmatriculadosmodulom'),

    #AULAS VIRTUALES
    path('miscursos/', aulavirtual_views.MisCursos, name='miscursos'),
    path('aulavirtualdocente/<int:programa_id>/<int:modulo_id>/', aulavirtual_views.AulaVirtual_Docente, name='aulavirtual_docente'),
    path('aulavirtualestudiante/<int:programa_id>/', aulavirtual_views.AulaVirtual_Estudiante, name='aulavirtual_estudiante'),

    #PERFECCIONAMIENTO DOCENTE
    ############################
    path("perfeccionamientodocente/", perfeccionamientodocente_views.perfeccionamientodocente, name="perfeccionamientodocente"),
    # Áreas conocimiento
    path("areasconocimiento/", perfeccionamientodocente_views.areas_list, name="pd_areasconocimiento_list"),
    path("areasconocimiento/crear/", perfeccionamientodocente_views.area_create, name="pd_areaconocimiento_create"),
    path("areasconocimiento/<int:area_id>/editar/", perfeccionamientodocente_views.area_update, name="pd_areaconocimiento_update"),
    path("areasconocimiento/<int:area_id>/eliminar/", perfeccionamientodocente_views.area_delete, name="pd_areaconocimiento_delete"),

    # Subáreas conocimiento
    path("subareasconocimiento/", perfeccionamientodocente_views.subareas_list, name="pd_subareasconocimiento_list"),
    path("subareasconocimiento/crear/", perfeccionamientodocente_views.subarea_create, name="pd_subareaconocimiento_create"),
    path("subareasconocimiento/<int:subarea_id>/editar/", perfeccionamientodocente_views.subarea_update, name="pd_subareaconocimiento_update"),
    path("subareasconocimiento/<int:subarea_id>/eliminar/", perfeccionamientodocente_views.subarea_delete, name="pd_subareaconocimiento_delete"),

    # Campos conocimiento
    path("camposconocimiento/", perfeccionamientodocente_views.campos_list, name="pd_camposconocimiento_list"),
    path("camposconocimiento/crear/", perfeccionamientodocente_views.campo_create, name="pd_campoconocimiento_create"),
    path("camposconocimiento/<int:campo_id>/editar/", perfeccionamientodocente_views.campo_update, name="pd_campoconocimiento_update"),
    path("camposconocimiento/<int:campo_id>/eliminar/", perfeccionamientodocente_views.campo_delete, name="pd_campoconocimiento_delete"),

    # PDCursos
    path("pdcursos/", perfeccionamientodocente_views.cursos_list, name="pd_cursos_list"),
    path("pdcursos/crear/", perfeccionamientodocente_views.curso_create, name="pd_curso_create"),
    path("pdcursos/<int:curso_id>/editar/", perfeccionamientodocente_views.curso_update, name="pd_curso_update"),
    path("pdcursos/<int:curso_id>/eliminar/", perfeccionamientodocente_views.curso_delete, name="pd_curso_delete"),
    path("ajax/subareas/", perfeccionamientodocente_views.ajax_subareas_por_area, name="pd_ajax_subareas_por_area"),
    path("ajax/campos/", perfeccionamientodocente_views.ajax_campos_por_subarea, name="pd_ajax_campos_por_subarea"),

    # Participantes PDCursos
    path("pdparticipantescursos/", perfeccionamientodocente_views.participantes_cursos_list, name="pd_participantescursos_list"),
    # Detalle por curso
    path("pdparticipantes/curso/<int:curso_id>/", perfeccionamientodocente_views.participantes_curso_detalle, name="pd_participantes_curso_detalle"),
    path("pdparticipantes/curso/<int:curso_id>/matricular/", perfeccionamientodocente_views.participantes_curso_matricular, name="pd_participantes_curso_matricular"),
    # Resultados y eliminar matrícula
    path("pdparticipantes/<int:participacion_id>/resultados/", perfeccionamientodocente_views.participantes_resultados_update, name="pd_participantes_resultados"),
    path("pdparticipantes/<int:participacion_id>/eliminar/", perfeccionamientodocente_views.participantes_matricula_delete, name="pd_participantes_eliminar"),

    # Reportes
    path("pdreportes/", perfeccionamientodocente_views.reportes_cursos_list, name="pd_reportes_list"),
    path("pdreportes/<int:curso_id>/pdf/", perfeccionamientodocente_views.reporte_curso_pdf, name="pd_reporte_curso_pdf"),
    ############################


    #TinyMCE
    ############################
    path('tinymce/', include('tinymce.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


