"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from rest_framework import permissions

schema_view = swagger_get_schema_view(
    openapi.Info(
        title = 'Bookify',
        default_version = '1.0.0',
        description = 'Bookify Swagger Schema'
    ),
    public = True,
    permission_classes=(permissions.AllowAny,),

)


urlpatterns = [
    # path('accounts/login/', views.MyTokenObtainPairView.as_view(),
    #     name='token_obtain_pair'),
    path('admin/', admin.site.urls),
    path('api/users/', include('api.urls.user_urls')),
    path('api/books/', include('api.urls.book_urls')),
    path('api/orders/', include('api.urls.order_urls')),
    path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0),
                            name='swagger-schema')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)