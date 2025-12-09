from django.db import models
from django.contrib.auth.models import User
from needy_app.models import NeedyCase


class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    case = models.ForeignKey(NeedyCase, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated {self.amount}"