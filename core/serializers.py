from rest_framework import serializers
from .models import League, Season, Matchday, Team, Game, Player, Stats, PlayerMetric

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

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = '__all__'


class PlayerMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMetric
        fields = '__all__'
