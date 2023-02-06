from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class DriverSelectForm(forms.Form):
    Drive_ride = forms.BooleanField(
        help_text="Are you sure you want to Drive the ride?")


class DriverCompleteForm(forms.Form):
    Complete_ride = forms.BooleanField(
        help_text="Are you sure you want to Mark the ride as complete?")


class SharerSelectForm(forms.Form):
    Sharer_ride = forms.BooleanField(
        help_text="Are you sure you want to Join the ride as a sharer?")


class SharerDeleteForm(forms.Form):
    sharer_leave = forms.BooleanField(
        help_text="Are you sure you want to leave the ride")


class CreateSharerform(forms.Form):
    destination = forms.CharField(
        required=True, help_text="Enter your destination")
    passenger_num = forms.IntegerField(
        help_text="Enter the passenager number from your party", required=True)
    earliest_time = forms.DateTimeField(
        help_text="Earliest time: (format:YYYY-MM-DD HH-MM)", required=True)
    latest_time = forms.DateTimeField(
        help_text="Latest time: (format:YYYY-MM-DD HH-MM)", required=True)
    temp = None

    def clean_passenger_num(self):
        data = self.cleaned_data['passenger_num']
        if data < 1 or data > 6:
            raise ValidationError(
                _('Invalid number - has to be in the range [1,6]'))
        return data

    def clean_earliest_time(self):
        data = self.cleaned_data['earliest_time']
        if data < timezone.now():
            raise ValidationError(_('Invalid date - search for past'))
        self.temp = data
        return data

    def clean_latest_time(self):
        latest_data = self.cleaned_data['latest_time']
        if latest_data < timezone.now():
            raise ValidationError(_('Invalid date - search for past'))

        if self.temp == None or latest_data < self.temp:
            raise ValidationError(
                _('Lastest time cannot be earlier than earliest time'))
        return latest_data
