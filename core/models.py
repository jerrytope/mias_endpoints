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
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="seasons")
    year = models.CharField(max_length=9)  # e.g., "2023/2024"
    max_substitutions = models.PositiveIntegerField(default=5)  # Specify before season starts
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['league', 'year'], name='unique_season_per_league')
        ]

    def __str__(self):
        return f"{self.league.name} - {self.year}"

# 3. Matchday Model
class Matchday(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matchdays")
    name = models.CharField(max_length=20)
    number = models.PositiveIntegerField()  # e.g., Matchday 1, Matchday 2
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['season', 'number'], name='unique_matchday_per_season')
        ]

    def __str__(self):
        return f"{self.season.year} - Matchday {self.number}"

# 4. Team Model
class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 5. Game Model
class Game(models.Model):
    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, related_name="games")
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_games")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_games")
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(home_team=models.F('away_team')), name='no_self_games')
        ]

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.matchday})"


from django.core.validators import MinValueValidator
class Player(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50)  # e.g., "Forward"
    age = models.PositiveIntegerField(null=True, blank=True)
    jersey_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Jersey number (1–99). Must be unique within the same team."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'jersey_number'],
                name='unique_jersey_per_team'
            )
        ]
        indexes = [
            models.Index(fields=['team', 'jersey_number'], name='idx_team_jersey')
        ]

    def __str__(self):
        return f"{self.name} ({self.team.name}) - #{self.jersey_number}"
    
# core/models.py
class Metric(models.Model):
    name = models.CharField(max_length=50, unique=True)
    short_code = models.CharField(max_length=10, unique=True)  # e.g., "SOT", "PASS"
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.short_code})"
    

# core/models.py
class PlayerGameStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'player', 'metric'],
                name='unique_player_stat_per_game'
            )
        ]
        indexes = [
            models.Index(fields=['game', 'player']),
            models.Index(fields=['metric']),
        ]

    def __str__(self):
        return f"{self.player} - {self.metric}: {self.count} ({self.game})"
    

# # 7. Stats Model (aggregated per player per game)
# class Stats(models.Model):
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="stats")
#     player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="stats")
#     goals = models.PositiveIntegerField(default=0)
#     assists = models.PositiveIntegerField(default=0)
#     shots_on_target = models.PositiveIntegerField(default=0)
#     tackles = models.PositiveIntegerField(default=0)
#     interceptions = models.PositiveIntegerField(default=0)
#     passes = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['game', 'player'], name='unique_stats_per_player_game')
#         ]

#     def __str__(self):
#         return f"Stats for {self.player.name} in {self.game}"

# # 8. PlayerMetric Model (for real-time metric collection)
# class PlayerMetric(models.Model):
#     METRIC_CHOICES = [
#         ('goal', 'Goal'),
#         ('assist', 'Assist'),  # Added this to match Stats
#         ('pass', 'Pass'),
#         ('sot', 'Shot On Target'),
#         ('tackle', 'Tackle'),
#         ('interception', 'Interception'),
#     ]
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)
#     metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
#     count = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['game', 'player', 'metric'], name='unique_metric_per_player_game')
#         ]

#     def __str__(self):
#         return f"{self.player.name} - {self.metric}: {self.count}"
    


# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=PlayerMetric)
# def update_stats(sender, instance, **kwargs):
    # stats, created = Stats.objects.get_or_create(game=instance.game, player=instance.player)
    # if instance.metric == 'goal':
    #     stats.goals = instance.count
    # elif instance.metric == 'assist':
    #     stats.assists = instance.count
    # # Add similar for others
    # stats.save()