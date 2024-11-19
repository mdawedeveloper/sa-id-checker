from django.db import models

# Create your models here.

class IDInfo(models.Model):
    id_number = models.CharField(max_length=13, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6)  # Male or Female
    is_sa_citizen = models.BooleanField()
    search_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.id_number
        
class SearchLog(models.Model):
    id_info = models.ForeignKey(IDInfo, related_name="search_logs", on_delete=models.CASCADE)
    search_date = models.DateField(auto_now_add=True)  # Automatically record the date of the search

    def __str__(self):
        return f"Search for {self.id_info.id_number} on {self.search_date}"

class PublicHoliday(models.Model):
    id_info = models.ForeignKey(IDInfo, related_name="holidays", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} on {self.date}"
