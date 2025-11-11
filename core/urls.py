from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *
from .views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'matchdays', MatchdayViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'games', GameViewSet)
router.register(r'players', PlayerViewSet)
# router.register(r'stats', StatsViewSet)
router.register(r'metrics', MetricViewSet)

urlpatterns = [
    # path('update-metric/', PlayerMetricUpdateView.as_view(), name='update-metric'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST username/password -> access/refresh tokens
    path('register/', RegisterView.as_view(), name='register'),
    path('player-stats/', PlayerGameStatUpdateView.as_view(), name='player-stats'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # POST refresh -> new access token
    path('', include(router.urls)),
]