from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import League, Season, Matchday, Team, Game, Player, Stats, PlayerMetric
from .serializers import (
    LeagueSerializer, SeasonSerializer, MatchdaySerializer,
    TeamSerializer, GameSerializer, PlayerSerializer, StatsSerializer, PlayerMetricSerializer
)
from .core import wrap_response
from .permissions import (
    IsSuperAdmin, IsSuperAdminOrAdmin, IsSuperAdminOrDataCollector,
    IsSuperAdminOrAdminOrDataCollector
)
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer   # <-- we will create this next
from .core import wrap_response



def viewset_with_wrapper(viewset_class):
    """
    Takes a ModelViewSet class and returns a new class where every action
    (list, retrieve, create, update, partial_update, destroy) is wrapped.
    """
    class WrappedViewSet(viewset_class):
        @wrap_response
        def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)

        @wrap_response
        def retrieve(self, request, *args, **kwargs):
            return super().retrieve(request, *args, **kwargs)

        @wrap_response
        def create(self, request, *args, **kwargs):
            return super().create(request, *args, **kwargs)

        @wrap_response
        def update(self, request, *args, **kwargs):
            return super().update(request, *args, **kwargs)

        @wrap_response
        def partial_update(self, request, *args, **kwargs):
            return super().partial_update(request, *args, **kwargs)

        @wrap_response
        def destroy(self, request, *args, **kwargs):
            return super().destroy(request, *args, **kwargs)

    return WrappedViewSet


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @wrap_response
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Optionally assign to a group (admin / data_collector)
        group_name = request.data.get("role")   # "admin" or "data_collector"
        if group_name in ["admin", "data_collector"]:
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        return Response(
            {"detail": "User registered successfully."},
            status=status.HTTP_201_CREATED,
        )
    


class LeagueViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class SeasonViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class MatchdayViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Matchday.objects.all()
    serializer_class = MatchdaySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class TeamViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class GameViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class PlayerViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

class StatsViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrDataCollector()]

class PlayerMetricUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrDataCollector]

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
        filters = {"player": player_id}
        if game_id:
            filters["game"] = game_id

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

        if not all([player_id, metric, game_id]):
            return Response({"error": "player_id, metric, and game_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get or create the PlayerMetric instance
            player_metric, created = PlayerMetric.objects.get_or_create(
                game_id=game_id, player_id=player_id, metric=metric
            )
            player_metric.count += value
            if player_metric.count < 0:
                player_metric.count = 0  # Prevent negative counts
            player_metric.save()

            # Optional: Aggregate to Stats model if desired (e.g., update Stats on save)
            # You could use Django signals for this in models.py

            return Response({"message": "Metric updated successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)