from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('medicamentos/', views.lista_medicamentos, name='lista_medicamentos'),
    path('medicamentos/crear/', views.crear_medicamento, name='crear_medicamento'),
    path('medicamentos/<int:pk>/editar/', views.editar_medicamento, name='editar_medicamento'),
    path('medicamentos/<int:pk>/eliminar/', views.eliminar_medicamento, name='eliminar_medicamento'),
    path('medicamentos/exportar/', views.exportar_a_excel, name='exportar_a_excel'),
]