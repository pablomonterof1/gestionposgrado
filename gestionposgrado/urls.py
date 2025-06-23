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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    path('programamaestria/<int:programa_id>/', main_views.ProgramaMaestria, name='programamaestria'),
    path('programasdemaestria/', main_views.programasdemaestria, name='programasdemaestria'),
    
    #Gestion de usuarios
    path('signup/', user_views.signup, name='signup'),
    path('perfil/', user_views.perfil, name='perfil'),
    path('logout/', user_views.signout, name='logout'),
    path('signin/', user_views.signin, name='signin'),
    path('gestionusuarios/', user_views.datosUsuario, name='gestionusuarios'),
    path('actualizar-rol/<int:usuario_id>/', user_views.actualizar_rol_usuario, name='actualizar_rol_usuario'),
    path('docentedp/create/<int:periodo_id>', user_views.docentedp_create, name='docentedp_create'),
    path('tutordp/create/<int:periodo_id>', user_views.tutordp_create, name='tutordp_create'),
    path('coordinadordp/create/<int:periodo_id>', user_views.coordinadordp_create, name='coordinadordp_create'),
    
    
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
    path('perfilingreso/', programasposgrado_views.perfildeingreso, name='perfilingreso'),
    path('programasdeposgrado/', programasposgrado_views.programasdeposgrado, name='programasdeposgrado'),
    path('programadeposgrado/select/', programasposgrado_views.programadeposgrado_select, name='programadeposgrado_select'),
    path('programadeposgrado/create/', programasposgrado_views.programadeposgrado_create, name='programadeposgrado_create'),
    path('programadeposgrado/<int:programadeposgrado_id>/delete', programasposgrado_views.programadeposgrado_delete, name='programadeposgrado_delete'),
    path('programadeposgrado/<int:programadeposgrado_id>', programasposgrado_views.programadeposgrado_update, name='programadeposgrado_update'),
    path('campoamplio/', programasposgrado_views.campoamplio, name='campoamplio'),

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


    #DATOSPOSGRADO
    path('periodosacademicosdp/', datosposgrado_views.periodosacademicosdp, name='periodosacademicosdp'),
    path('datosposgrado/<int:periodo_id>/', datosposgrado_views.datosposgrado, name='datosposgrado'),
    #Contratos docentes
    path('contratosdocentes/<int:periodo_id>/', datosposgrado_views.contratosdocentes, name='contratosdocentes'),
    path('contratosdocentes/create/<int:periodo_id>', datosposgrado_views.contratosdocentes_create, name='contratosdocentes_create'),
    path('contratosdocentesupdate/<int:contratosdocentes_id>/<int:periodo_id>', datosposgrado_views.contratosdocentes_update, name='contratosdocentes_update'),
    path('contratosdocentes/<int:contratosdocentes_id>/<int:periodo_id>/delete', datosposgrado_views.contratosdocentes_delete, name='contratosdocentes_delete'),
    path('api/modulos/<int:programa_id>/', datosposgrado_views.obtener_modulos_por_maestria, name='obtener_modulos_por_maestria'),
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
    #Seleccion de perfiles
    path('seleccionp/', seleccionperfiles_views.seleccionp, name='seleccionp'),
    path('periodosacademicosp/', seleccionperfiles_views.periodosacademicosp, name='periodosacademicosp'),    
    path('datosposgradosp/<int:periodo_id>/', seleccionperfiles_views.datosposgradosp, name='datosposgradosp'),
    path('datosmodulos/<int:programa_id>/', seleccionperfiles_views.datosmodulos, name='datosmodulos'),
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


    ############################


    #TinyMCE
    ############################
    path('tinymce/', include('tinymce.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


