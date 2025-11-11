from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group

# yourapp/serializers.py   (add / replace)

from django.contrib.auth.models import User, Group
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    role = serializers.ChoiceField(
        choices=[
            ("super_admin", "Super Admin"),
            ("admin", "Admin"),
            ("data_collector", "Data Collector"),
        ],
        required=True,
        help_text="Required: super_admin | admin | data_collector"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "role")

    def create(self, validated_data):
        role = validated_data.pop("role")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)

        # ---- SUPER ADMIN -------------------------------------------------
        if role == "super_admin":
            user.is_superuser = True
            user.is_staff = True          # needed for admin access
        # ---- SAVE USER ---------------------------------------------------
        user.save()

        # ---- GROUPS ------------------------------------------------------
        if role != "super_admin":        # super_admin does not need a group
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        return user
    


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'

class MatchdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Matchday
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


# core/serializers.py
class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ['id', 'name', 'short_code', 'description']


# class PlayerGameStatSerializer(serializers.ModelSerializer):
#     metric = MetricSerializer(read_only=True)
#     metric_id = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = PlayerGameStat
#         fields = ['id', 'metric', 'metric_id', 'count', 'created_at', 'updated_at']

# core/serializers.py
class PlayerGameStatSerializer(serializers.ModelSerializer):
    metric = serializers.CharField(source='metric.name')
    metric_short_code = serializers.CharField(source='metric.short_code')
    player_name = serializers.CharField(source='player.name')
    player_jersey = serializers.IntegerField(source='player.jersey_number')
    game_date = serializers.DateTimeField(source='game.date', format="%Y-%m-%d %H:%M")

    class Meta:
        model = PlayerGameStat
        fields = [
            'id', 'player_name', 'player_jersey',
            'metric', 'metric_short_code',
            'count', 'game_date', 'created_at', 'updated_at'
        ]

class PlayerSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'position', 'jersey_number', 'stats']

    def get_stats(self, obj):
        game_id = self.context.get('game_id')
        if not game_id:
            return {}

        stats = PlayerGameStat.objects.filter(player=obj, game_id=game_id)
        return {
            stat.metric.short_code.lower(): stat.count
            for stat in stats
        }
    


