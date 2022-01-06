from django.db import models

# we're going to be using a special method to find our user model
from django.contrib.auth import get_user_model
# we dont want to directly import our user model, we want to use this method instead.

# Create your models here.
class Mango(models.Model):
  # define fields
  # https://docs.djangoproject.com/en/3.0/ref/models/fields/
  name = models.CharField(max_length=100)
  ripe = models.BooleanField()
  color = models.CharField(max_length=100)
  # For user ownership, we'll add a new field 'owner' which keeps track
  # of the user id who owns this the mango
  owner = models.ForeignKey(
    get_user_model(),
    on_delete=models.CASCADE
  )

  def __str__(self):
    # This must return a string
    return f"The mango named '{self.name}' is {self.color} in color. It is {self.ripe} that it is ripe."

  def as_dict(self):
    """Returns dictionary version of Mango models"""
    return {
        'id': self.id,
        'name': self.name,
        'ripe': self.ripe,
        'color': self.color
    }
