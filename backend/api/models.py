from django.db import models

# Create your models here.
from django.db import models

class Project(models.Model):
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location_size = models.FloatField()

    def __str__(self):
        return f"Project - Budget: ${self.budget}, Location: {self.location_size} sqft"

