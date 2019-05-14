from django.db import models
import numpy as np
from django.contrib.auth.models import User

# or Movies
class Wine(models.Model):
    name = models.CharField(max_length=200)
    genres = models.CharField(max_length=200, default='unspecified')
    poster_path = models.CharField(max_length=500, default='unspecified')
    
    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        mean_ratings = np.mean(list(all_ratings))
        return mean_ratings
        
    def __unicode__(self):
        return self.name


class Fake(models.Model):
    actual_id = models.IntegerField(
        default=max(list(User.objects.values_list('id', flat = True))) + 1)

    fake_id = models.AutoField(primary_key=True, default=User.objects.count())

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    wine = models.ForeignKey(Wine,
                             on_delete=models.CASCADE,)
    pub_date = models.DateTimeField('date published')
    user_id = models.IntegerField(default=User.objects.count())
    user_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=200)
    rating = models.IntegerField(choices=RATING_CHOICES)
    
# The below class is not used anymore.
class Cluster(models.Model):

    # For a cluster, we store a name and a list of users.
    # We leave the door open for users to belong to more than one cluster by using that ManyToManyField. 
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)

    # We also define a method to get all the member user names get_memebers.
    def get_members(self):
        return "\n".join([u.username for u in self.users.all()])