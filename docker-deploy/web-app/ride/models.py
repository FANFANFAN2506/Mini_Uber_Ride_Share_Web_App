from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
import uuid  # Required for unique book instances
from django.db import models


class Driver(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    liscense_plate = models.CharField(
        max_length=7, unique=True, help_text='Enter your liscense plate', blank=False)

    max_num_passengers = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(6)], blank=False)

    VEHICLE = (
        ('Sedan', 'Sedan'),
        ('Coupe', 'Coupe'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV')
    )
    vehicle_type = models.CharField(
        max_length=10,
        choices=VEHICLE,
        blank=False,
        null=False,
        default='Sedan',
        help_text='Vehicle type'
    )

    special_request = models.TextField(
        max_length=200, blank=True, help_text="E.g Assistance")

    def get_user(self):
        return self.user

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('driver-detail', args=[str(self.id)])

    def __str__(self):
        return self.liscense_plate


class Ride(models.Model):
    # Unique ride id
    ride_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                               help_text="Unique ID for the ride")
    destination_addr = models.CharField(max_length=20, blank=False)
    arrival_date = models.DateTimeField(
        null=False, blank=False, default=datetime.now)
    passenger_num = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(6)], blank=False)

    VEHICLE = (
        ('Sedan', 'Sedan'),
        ('Coupe', 'Coupe'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV')
    )
    vehicle_type = models.CharField(
        max_length=100,
        choices=VEHICLE,
        blank=True,
        null=True,
        default='Sedan',
        help_text='Vehicle type'
    )

    RIDE_STATUS = (
        ('open', 'open'),
        ('confirmed', 'confirmed'),
        ('complete', 'complete')
    )

    status = models.CharField(
        max_length=100,
        choices=RIDE_STATUS,
        blank=False,
        default='open',
        help_text='Ride status'
    )

    special_request = models.TextField(
        max_length=1000, blank=True, null=True, help_text="E.g. Assistance")

    if_share = models.BooleanField(default=False)

    # User related info:
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=False)

    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_open(self):
        return bool(self.status == 'open')

    @property
    def is_confirmed(self):
        return bool(self.status == 'confirmed')

    @property
    def is_complete(self):
        return bool(self.status == 'complete')

    def get_absolute_url(self):
        return reverse('ride-detail', args=[str(self.ride_id)])

    def __str__(self):
        if self.owner:
            name = self.owner.get_username()
        else:
            name = ""
        return self.destination_addr+" "+str(self.arrival_date)+" "+name


class Sharer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    passenger_num = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(6)], blank=False)
    ride_joined = models.ForeignKey(
        Ride, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.get_username()+" "+str(self.passenger_num)
