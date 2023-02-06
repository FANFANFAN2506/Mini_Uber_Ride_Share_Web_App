from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from .forms_ride import NewUserForm, CreateSharerform, DriverSelectForm, SharerDeleteForm, DriverCompleteForm
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from ride.models import Ride, Driver, Sharer
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def index(request):
    return render(request, 'index.html')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registration successful.")
            return HttpResponseRedirect(reverse('home'))
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="register.html", context={"register_form": form})


@login_required
def user_home_view(request):
    return render(request, 'user_home.html')


@login_required
def RideListView(request):
    own_ride = Ride.objects.filter(owner=request.user)
    open_ride = own_ride.filter(status='open')
    confirmed_ride = own_ride.filter(status='confirmed')
    complete_ride = own_ride.filter(status='complete')
    drive_info = Driver.objects.filter(user=request.user)
    shared_ride = Sharer.objects.filter(user=request.user)

    if drive_info:
        drive_info = drive_info[0]
    return render(request, 'ride/ride_list.html', context={
        'own_ride': own_ride,
        'shared_ride': shared_ride,
        'open_ride': open_ride,
        'confirmed_ride': confirmed_ride,
        'complete_ride': complete_ride,
        'drive_info': drive_info,
    })


@login_required
def ride_detail_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    sharer_instance = Sharer.objects.filter(ride_joined=ride)
    is_owner = False
    is_driver = False
    owner_num = ride.passenger_num
    if ride.driver:
        if ride.driver.user == request.user:
            is_driver = True
    if sharer_instance:
        for sharer in sharer_instance:
            owner_num = owner_num - sharer.passenger_num
    if ride.owner == request.user:
        is_owner = True
    context = {
        'ride': ride,
        'is_owner': is_owner,
        'is_driver': is_driver,
        'owner_num': owner_num,
        'sharer_instance': sharer_instance,
    }
    return render(request, 'ride/ride_detail.html', context)


class RequestRide(LoginRequiredMixin, CreateView):
    model = Ride
    fields = ['destination_addr', 'arrival_date', 'passenger_num',
              'vehicle_type', 'special_request', 'if_share']
    error_message = "Request ride in the past!"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        if form.instance.arrival_date < timezone.now():
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, self.error_message)
        return super().form_invalid(form)


class RideUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ride
    fields = ['destination_addr', 'arrival_date', 'passenger_num',
              'vehicle_type', 'special_request', 'if_share']
    error_message = "Request ride in the past!"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        if form.instance.arrival_date < timezone.now():
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)

    def test_func(self):
        ride_owner = self.get_object()
        if self.request.user == ride_owner.owner:
            return True
        return False


class RideDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ride
    success_url = reverse_lazy('rides')

    def test_func(self):
        ride_owner = self.get_object()
        if self.request.user == ride_owner.owner:
            return True
        return False


@login_required
def drive_menu_view(request):
    drive_info = Driver.objects.filter(user=request.user).first()
    return render(request, 'ride/driver_menu.html', context={'drive': drive_info})


class DriverCreate(LoginRequiredMixin, CreateView):
    model = Driver
    fields = ['liscense_plate', 'max_num_passengers',
              'vehicle_type', 'special_request']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def DriverDetailView(request, pk):
    driver_info = get_object_or_404(Driver, pk=pk)
    return render(request, 'ride/driver_detail.html', context={
        'driver_info': driver_info,
    })


class DriverUpdate(LoginRequiredMixin, UpdateView):
    model = Driver
    fields = ['liscense_plate', 'max_num_passengers',
              'vehicle_type', 'special_request']


@login_required
def DriveListView(request, pk):
    drive_info = get_object_or_404(Driver, pk=pk)
    ride_drive = drive_info.ride_set.all()
    confirmed_drive = ride_drive.filter(status='confirmed')
    complete_drive = ride_drive.filter(status='complete')
    return render(request, 'ride/driver_list.html', context={
        'ride_drive': ride_drive,
        'confirmed_drive': confirmed_drive,
        'complete_drive': complete_drive,
    })


@login_required
def DriverSearchView(request, pk):
    drive_infor = get_object_or_404(Driver, pk=pk)
    sharer_instance = Sharer.objects.filter(user=request.user)
    v_type = drive_infor.vehicle_type
    max_passeng_num = drive_infor.max_num_passengers
    special = drive_infor.special_request
    valid_ride = Ride.objects.filter(status='open').exclude(owner=request.user).filter(
        passenger_num__lte=max_passeng_num).filter(Q(vehicle_type=None) | Q(vehicle_type=v_type)).filter(Q(special_request="") | Q(special_request=special)).order_by('arrival_date')
    if sharer_instance:
        for sharer in sharer_instance:
            valid_ride = valid_ride.exclude(ride_id=sharer.ride_joined.ride_id)
    context = {
        'valid_ride': valid_ride,
    }
    return render(request, 'ride/driver_search.html', context)


@login_required
def DriverConfirmView(request, id):
    ride_instance = get_object_or_404(Ride, ride_id=id)
    if request.method == 'POST':
        form = DriverSelectForm(request.POST)
        if form.is_valid():
            ride_instance.status = 'confirmed'
            ride_instance.driver = request.user.driver
            ride_instance.save()
            send_mail(
                'Congratulations!',
                'Your ride with '+str(request.user)+' To ' +
                str(ride_instance.destination_addr)+" has been confirmed",
                'yangfan1670@163.com',
                [ride_instance.owner.email],
                fail_silently=False,
            )
            if ride_instance.sharer_set.all():
                for sharer_instance in ride_instance.sharer_set.all():
                    send_mail(
                        'Congratulations!',
                        'Your ride with ' +
                        str(request.user)+' To ' +
                        str(ride_instance.destination_addr) +
                        " has been confirmed",
                        'yangfan1670@163.com',
                        [sharer_instance.user.email],
                        fail_silently=False,
                    )
        return HttpResponseRedirect(reverse('driver'))
    else:
        form = DriverSelectForm()
    context = {
        'id': id,
        'form': form,
        'ride_instance': ride_instance,
    }
    return render(request, 'ride/driver_confirm.html', context)


@login_required
def DriverCompleteView(request, id):
    ride_instance = get_object_or_404(Ride, ride_id=id)
    if request.method == 'POST':
        form = DriverCompleteForm(request.POST)
        if form.is_valid():
            ride_instance.status = 'complete'
            ride_instance.save()
        return HttpResponseRedirect(reverse('driver'))
    else:
        form = DriverCompleteForm()
    context = {
        'id': id,
        'form': form,
        'ride_instance': ride_instance,
    }
    return render(request, 'ride/driver_complete.html', context)


@login_required
def SharerfindView(request):
    sharer_create = Sharer(user=request.user)
    if request.method == "POST":
        form = CreateSharerform(request.POST)
        if form.is_valid():
            sharer_create.destination_addr = form.cleaned_data['destination']
            sharer_create.earliest_date = form.cleaned_data['earliest_time']
            sharer_create.latest_date = form.cleaned_data['latest_time']
            sharer_create.passenger_num = form.cleaned_data['passenger_num']
            max_vehicle_num = 6 - sharer_create.passenger_num
            sharer_exist = Sharer.objects.filter(user=request.user)
            valid_ride = Ride.objects.filter(if_share=True).filter(
                status='open').filter(arrival_date__lte=sharer_create.latest_date).exclude(owner=request.user)
            valid_ride = valid_ride.filter(arrival_date__gte=sharer_create.earliest_date).filter(
                destination_addr=sharer_create.destination_addr).filter(passenger_num__lte=max_vehicle_num)
            if sharer_exist:
                for share_instnace in sharer_exist:
                    valid_ride = valid_ride.exclude(
                        ride_id=share_instnace.ride_joined.ride_id)
            context = {
                'valid_ride': valid_ride,
                'sharer_create': sharer_create,
                'sharer_exist': sharer_exist,
                'pass_num': sharer_create.passenger_num,
            }
            return render(request, 'ride/sharer_search.html', context)
    else:
        form = CreateSharerform()
    context = {
        'form': form,
    }
    return render(request, 'ride/sharer_form.html', context)


@login_required
def SharerJoinView(request, num):
    sharer_create = Sharer(user=request.user)
    sharer_create.passenger_num = num

    ride_instance = get_object_or_404(
        Ride, ride_id=request.POST['ride_id_select'])
    sharer_create.ride_joined = ride_instance
    ride_instance.passenger_num += num
    ride_instance.save()
    sharer_create.save()
    return render(request, 'ride/join_confirm.html', context={'sharer_create': sharer_create, 'ride_instance': ride_instance})


@login_required
def SharerDeleteView(request, id):
    ride_instance = get_object_or_404(Ride, ride_id=id)
    sharer_instance = get_object_or_404(
        Sharer, user=request.user, ride_joined=ride_instance)
    if request.method == 'POST':
        form = SharerDeleteForm(request.POST)
        if form.is_valid():
            ride_instance.sharer = None
            ride_instance.passenger_num -= sharer_instance.passenger_num
            sharer_instance.delete()
            ride_instance.save()
            return HttpResponseRedirect(reverse('rides'))
    else:
        form = SharerDeleteForm()
    context = {
        'form': form,
        'ride_instance': ride_instance,
    }
    return render(request, 'ride/sharer_delete.html', context)
