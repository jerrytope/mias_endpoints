from rest_framework import serializers
from .models import League, Season, Matchday, Team, Game, Player, Stats, PlayerMetric
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