from django.db import models

# Create your models here.
class AvailableRoles(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.role_name)

class SelectedRoles(models.Model):
    role_name = models.CharField(max_length=50)
    player_first = models.CharField(max_length=50, null=True)
    player_last = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return 'Player: ' + str(self.player_name) + '\t' + \
                'Role: ' + str(self.role_name)

class User(models.Model):
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)
    phone_number = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return 'Name: ' + str(self.first_name) + ' ' + str(self.last_name) + \
                '\t Number: ' + str(self.phone_number)
    

