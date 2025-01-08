from django.db import models

# Create your models here.
from django.db import models

# 1. League Model
class League(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 2. Season Model
class Season(models.Model):
    # league_id = models.ForeignKey(League, on_delete=models.CASCADE, related_name="seasons")
    year = models.CharField(max_length=9)  # e.g., "2023/2024"
    max_substitutions = models.PositiveIntegerField(default=5)  # Specify before season starts
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.league.name} - {self.year}"


# 3. Matchday Model
class Matchday(models.Model):
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matchdays")
    name = models.CharField(max_length=20)
    number = models.PositiveIntegerField()  # e.g., Matchday 1, Matchday 2
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.season.year} - Matchday {self.number}"


# 4. Team Model
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    league_id = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 5. Game Model
class Game(models.Model):
    matchday_id = models.ForeignKey(Matchday, on_delete=models.CASCADE, related_name="games")
    home_team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_games")
    away_team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_games")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.matchday})"


# 6. Player Model
class Player(models.Model):
    name = models.CharField(max_length=255)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50)  # e.g
    age = models.PositiveIntegerField(null =True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    	return f"{self.name} ({self.team.name})"


class Stats(models.Model): 
	game_id = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="stats") 
	player_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="stats") 
	goals = models.PositiveIntegerField(default=0) 
	assists = models.PositiveIntegerField(default=0) 
	shots_on_target = models.PositiveIntegerField(default=0) 
	tackles = models.PositiveIntegerField(default=0) 
	interceptions = models.PositiveIntegerField(default=0) 
	passes = models.PositiveIntegerField(default=0) 
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Stats for {self.player.name} in {self.game}"


class PlayerMetric(models.Model):
    METRIC_CHOICES = [
        ('goal', 'Goal'),
        ('pass', 'Pass'),
        ('sot', 'Shot On Target'),
        ('tackle', 'Tackle'),
        ('interception', 'Interception'),
    ]

    metric_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player.name} - {self.metric}: {self.count}"


