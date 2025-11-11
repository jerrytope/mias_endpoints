from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *
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

# class PlayerViewSet(viewset_with_wrapper(ModelViewSet)):
#     queryset = Player.objects.all()
#     serializer_class = PlayerSerializer

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             return [IsAuthenticated()]
#         return [IsAuthenticated(), IsSuperAdminOrAdmin()]
# core/views.py
class PlayerViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdminOrAdmin()]

    # ← ADD THIS METHOD
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['game_id'] = self.request.query_params.get('game_id')
        return context
    


# core/views.py
class MetricViewSet(viewset_with_wrapper(ModelViewSet)):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrAdmin]



# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import PlayerGameStat, Metric
from .serializers import PlayerGameStatSerializer
from .permissions import IsSuperAdminOrDataCollector
from .core import wrap_response  # your wrapper


class PlayerGameStatUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrDataCollector]

    @wrap_response
    def get(self, request):
        """
        GET: Retrieve PlayerGameStat records
        Filters:
          ?game_id=5
          ?player_id=10
          ?game_id=5&player_id=10
        """
        game_id = request.query_params.get("game_id")
        player_id = request.query_params.get("player_id")

        if not game_id and not player_id:
            return Response(
                {"error": "At least one of game_id or player_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = PlayerGameStat.objects.all()

        if game_id:
            queryset = queryset.filter(game_id=game_id)
        if player_id:
            queryset = queryset.filter(player_id=player_id)

        # Optional: order by metric
        queryset = queryset.select_related('metric', 'player', 'game').order_by('metric__name')

        serializer = PlayerGameStatSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @wrap_response
    def post(self, request):
        player_id = request.data.get("player_id")
        game_id = request.data.get("game_id")
        metric_id = request.data.get("metric_id")
        value = int(request.data.get("value", 1))

        if not all([player_id, game_id, metric_id]):
            return Response(
                {"error": "player_id, game_id, and metric_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            metric = Metric.objects.get(id=metric_id)
        except Metric.DoesNotExist:
            return Response(
                {"error": "Invalid metric_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        stat, created = PlayerGameStat.objects.get_or_create(
            player_id=player_id,
            game_id=game_id,
            metric_id=metric_id,
            defaults={'count': 0}
        )

        stat.count = F('count') + value
        stat.save()
        stat.refresh_from_db()

        return Response({
            "message": f"{metric.name} updated",
            "player": stat.player.name,
            "count": stat.count,
            "game_id": game_id,
            "metric_id": metric_id
        }, status=status.HTTP_200_OK)


