from django.urls import path
from .views import CustomLoginView, exportar_resultados_excel
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('crear-campaña/', views.crear_campaña, name='crear_campaña'),
    path('lista-campañas/', views.lista_campañas, name='lista-campañas'),
    path('campaña/<int:id>/editar/', views.editar_campaña, name='editar_campaña'),
    path('campañas/<int:id>/eliminar/', views.eliminar_campaña, name='eliminar_campaña'),

    #Listas y actividades
    path('listas/', views.listar_listas_crear, name='listar_listas'),
    path('editar-lista/<int:lista_id>/', views.editar_lista, name='editar_lista'),
    path('eliminar-lista/<int:id>/', views.eliminar_lista, name='eliminar_lista'),
    
    #Votantes
    path('', views.panel_votante, name='panel_votante'),
    path('votar/<int:lista_id>/', views.votar_lista, name='votar_lista'),
    
    #Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/exportar/excel/', exportar_resultados_excel, name='exportar_resultados_excel'),
    
    #Lista de votantes
    path('votantes/', views.lista_votantes, name='lista_votantes'),
    path('votante/crear/', views.crear_votante, name='crear_votante'),
    path('votante/eliminar_ajax/<int:votante_id>/', views.eliminar_votante_ajax, name='eliminar_votante_ajax'),
    path('importar-votantes/', views.importar_votantes, name='importar_votantes'),
    
    #Limpiar votaciones
    path('limpiar-votaciones/', views.limpiar_votaciones, name='limpiar_votaciones'),
    path('obtener-datos-grafico/', views.obtener_datos_grafico, name='obtener_datos_grafico'),  
      
]
