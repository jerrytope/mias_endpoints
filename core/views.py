from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response




from rest_framework.viewsets import ModelViewSet
from .models import League, Season, Matchday, Team, Game, Player, Stats
from .serializers import (
    LeagueSerializer, SeasonSerializer, MatchdaySerializer,
    TeamSerializer, GameSerializer, PlayerSerializer, StatsSerializer
)

class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

class SeasonViewSet(ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

class MatchdayViewSet(ModelViewSet):
    queryset = Matchday.objects.all()
    serializer_class = MatchdaySerializer

class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class StatsViewSet(ModelViewSet):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Player, PlayerMetric
from .serializers import GameSerializer, PlayerSerializer, PlayerMetricSerializer

# class PlayerMetricUpdateView(APIView):
#     def post(self, request):
#         # Retrieve the player and metric data
#         player_id = request.data.get("player_id")
#         metric = request.data.get("metric")
#         game_id = request.data.get("game_id")
#         value = int(request.data.get("value", 1))  # Default to +1 if not specified

#         try:
#             # Get or create the PlayerMetric instance
#             player_metric, created = PlayerMetric.objects.get_or_create(
#                 game_id=game_id, player_id=player_id, metric=metric
#             )
#             player_metric.count += value
#             player_metric.save()

#             return Response({"message": "Metric updated successfully!"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Player, PlayerMetric
from .serializers import PlayerMetricSerializer

class PlayerMetricUpdateView(APIView):
    # Handle GET requests to retrieve all metrics for a player
    def get(self, request):
        player_id = request.query_params.get("player_id")
        game_id = request.query_params.get("game_id")  # Optional, for filtering by game

        if not player_id:
            return Response(
                {"error": "player_id is required to retrieve metrics."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter by player and optionally by game
        filters = {"player_id": player_id}
        if game_id:
            filters["game_id"] = game_id

        metrics = PlayerMetric.objects.filter(**filters)
        serializer = PlayerMetricSerializer(metrics, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle POST requests to update a metric
    def post(self, request):
        # Retrieve the player and metric data
        player_id = request.data.get("player_id")
        metric = request.data.get("metric")
        game_id = request.data.get("game_id")
        value = int(request.data.get("value", 1))  # Default to +1 if not specified

        try:
            # Get or create the PlayerMetric instance
            player_metric, created = PlayerMetric.objects.get_or_create(
                game_id=game_id, player_id=player_id, metric=metric
            )
            player_metric.count += value
            player_metric.save()

            return Response({"message": "Metric updated successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
