from django.db import models

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import make_aware


class CodingUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="", blank=True)
    game_win = models.IntegerField(default=0)
    game_lose = models.IntegerField(default=0)
    age = models.IntegerField()
    bio = models.CharField(max_length=420)
    create_time = models.DateTimeField(auto_now_add=True)
    winning_rate = models.FloatField(default=0.0)

    def save(self):
        if self.game_win + self.game_lose == 0:
            self.winning_rate = 0
        else:
            self.winning_rate = self.game_win / (self.game_win + self.game_lose)
        super(CodingUser, self).save()

    def __str__(self):
        return self.user.username


class Room(models.Model):
    room_status = models.CharField(max_length=30)
    room_owner = models.ForeignKey(CodingUser, null=False, on_delete=models.CASCADE, related_name='room_ower_user')
    room_slogan = models.CharField(max_length=100, default="come on to battle!", null=True)
    user1 = models.ForeignKey(CodingUser, null=False, on_delete=models.CASCADE, related_name='room_user1')
    user2 = models.ForeignKey(CodingUser, null=True, on_delete=models.CASCADE, related_name='room_user2')
    user3 = models.ForeignKey(CodingUser, null=True, on_delete=models.CASCADE, related_name='room_user3')
    user4 = models.ForeignKey(CodingUser, null=True, on_delete=models.CASCADE, related_name='room_user4')
    user1_state = models.CharField(max_length=30, null=True)
    user2_state = models.CharField(max_length=30, null=True)
    user3_state = models.CharField(max_length=30, null=True)
    user4_state = models.CharField(max_length=30, null=True)


class invitation(models.Model):
    room_id = models.ForeignKey(Room, null=False, on_delete=models.CASCADE, related_name='room')
    invitor = models.ForeignKey(CodingUser, null=False, on_delete=models.CASCADE, related_name='invitor')
    invitee = models.ForeignKey(CodingUser, null=False, on_delete=models.CASCADE, related_name='invitee')
    message = models.CharField(max_length=70)
    state = models.CharField(max_length=30, null=True)
