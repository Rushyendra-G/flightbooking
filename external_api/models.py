from django.db import models

class ExternalAPISync(models.Model):
    provider = models.CharField(max_length=50)
    api_type = models.CharField(max_length=50)
    last_sync = models.DateTimeField()
    status = models.CharField(max_length=20)
    details = models.JSONField()

class ExternalTBOCountry(models.Model):
    provider = models.CharField(max_length=50)
    provider_country_code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ExternalTBOCity(models.Model):
    provider = models.CharField(max_length=50)
    provider_city_code = models.CharField(max_length=20)
    country = models.ForeignKey(ExternalTBOCountry, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ExternalTBOHotel(models.Model):
    provider = models.CharField(max_length=50)
    provider_hotel_code = models.CharField(max_length=20)
    city = models.ForeignKey(ExternalTBOCity, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=200)
    rating = models.CharField(max_length=10)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    facilities = models.JSONField()
    attractions = models.JSONField()
    description = models.TextField()
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ExternalTBOFlightToken(models.Model):
    provider = models.CharField(max_length=50)
    token_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        get_latest_by = 'created_at'
