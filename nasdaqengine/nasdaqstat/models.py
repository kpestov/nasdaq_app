from django.db import models


class Historical(models.Model):
    ticker = models.ForeignKey('Company', null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return 'volume={}'.format(str(self.volume))


class Company(models.Model):
    ticker = models.CharField(max_length=40)

    def __str__(self):
        return self.ticker
