from django.urls import path
from routing_app.views import HealthCheckView, GeocodeView, RoutePlanView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('geocode/', GeocodeView.as_view(), name='geocode'),
    path('routes/plan/', RoutePlanView.as_view(), name='route_plan'),
]
