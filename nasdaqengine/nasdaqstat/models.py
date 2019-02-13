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


class Insider(models.Model):
    name = models.CharField(max_length=40)
    relation = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class InsiderTrades(models.Model):
    ticker = models.ForeignKey('Company', null=True, blank=True, on_delete=models.CASCADE)
    insider = models.ForeignKey('Insider', null=True, blank=True, on_delete=models.CASCADE)
    last_date = models.DateField()
    transaction_type = models.CharField(max_length=60)
    owner_type = models.CharField(max_length=40)
    shares_traded = models.FloatField()
    last_price = models.FloatField(null=True, blank=True)
    shares_held = models.FloatField()

    def __str__(self):
        return '{} - {} - {}'.format(self.ticker, self.insider, self.last_date)




