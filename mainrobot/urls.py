from django.urls import path
from . import views

urlpatterns = [
    path('', views.load_product , name='products'),
    path('products/', views.load_product , name='products'),
    path('products/product_details/<int:id>',views.load_product_details , name='product_details'),
    
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout') ,
    path('dashboard/', views.admin_dashboard , name='admin_dashboard'),
    path('dashboard/manageusers' , views.manage_users , name = 'manageusers')
]

