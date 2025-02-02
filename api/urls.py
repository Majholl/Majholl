from django.urls import path
from api import view

urlpatterns = [
    path('get_users', view.get_all_users),
    path('docs' , view.schema_view.with_ui('swagger' , cache_timeout=0))
]