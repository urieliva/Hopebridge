from django.db import models
from django.contrib.auth.models import User

class NeedyCase(models.Model):
    # Renamed 'user' to 'needy' to match your View logic
    needy = models.ForeignKey(User, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    
    # Renamed 'story' to 'description' to match your Form
    description = models.TextField()
    
    # Made optional (blank=True) so you can test without uploading files first
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_approved = models.BooleanField(default=False)
    
    # Renamed 'created_at' to 'date_created' to match your Profile sort order
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title