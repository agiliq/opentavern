from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=40)
    group_type = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    members_name = models.CharField(max_length=40)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name
