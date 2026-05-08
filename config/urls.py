from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Modules métier
    path('api/geo/', include('apps.geo.urls')),
    path('api/referentiels/', include('apps.referentiels.urls')),
    path('api/acteurs/', include('apps.acteurs.urls')),
    path('api/projets/', include('apps.projets.urls')),
    path('api/marches/', include('apps.marches.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/ia/', include('apps.ia.urls')),
    path('api/export/', include('apps.marches.export_urls')),

    # Documentation OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
