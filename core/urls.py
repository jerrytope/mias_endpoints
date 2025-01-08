from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    LeagueViewSet, SeasonViewSet, MatchdayViewSet,
    TeamViewSet, GameViewSet, PlayerViewSet, StatsViewSet,PlayerMetricUpdateView
)

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'matchdays', MatchdayViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'games', GameViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'stats', StatsViewSet)

# urlpatterns = router.urls
urlpatterns = [
    path('update-metric/', PlayerMetricUpdateView.as_view(), name='update-metric'),
    # path('player-metrics/', PlayerMetricsView.as_view(), name='player-metrics'),
    path('', include(router.urls)),
]