# ***Danger log for Ride Sharing Service app:***
There are three mean roles in this app which are **riders, sharers, and drivers**. For the models design, these three are also the model class included in the whole structure. In addition, the development is divided into these parts achieved steps by steps with validation and test. As a result, the danger log will be noted and delivered according to these three parts seperately, presented in which development detect them.  
***
## ***Owner(Ride)***
For the first and the main model class is the Ride, this is the class associated with the request delcration and information. Here we need to implement the Ride request, Ride modification, Ride Delete, and Joined *(Sharer related)*, Confirm, Complete *(Driver related)*. There will be some situations that encounted bugs during the development: <br>
1. For the Ride there are some optional specification like *vehicle type*, and *special request*. This two are hard to define, and has to be perfectly match, which will make the filtering search and format matching hard to implement. In addition, to avoid this kind of randomness, we keep the **vehicle** as a choice filed, limited to the mainstream vehicle type in the market. 
2. Additionally, the special request will be provided a template *(Assistance)*, this could help to build some cohesion for mathcing. For the matching when some search are implemented, this special request ***TextField*** may cause some problems. As for the other field, like ***CharField***:vehicle type, if the unspecified ride could be matched with either the ***None*** type or any of the Driver's vehicle type which will return a successful match. However, for the ***TextField***, instead of matching with ***None***, the unspecified request should be match with an empty string ***""***, only which a successful filter will be returned.
```python
.filter(Q(vehicle_type=None) | Q(vehicle_type=v_type)).filter(Q(special_request="")
```
3. For the Ride request and modified views, there is something we don't want to expose to the user to change, we have to **hide** it from the views, that is the user associated with the ride, we need to explicit set the current user as the owner of this ride, and hide the sharer and driver field for later assignment. 
4. For the Ride request, it should have a clean data format which shouldn't allow user to specify a ride for the date before ***Today***, which will be nonesense. As other fields like **IntegerField**, we could specify a **minValueValidator**, however, there is no such thing in **DateTimefield**. As a result, we need to have some constrains in the form that is used for inputs. The best way to handle it is to customize the update and create view, which supports a self-constructed clean data, instead of using the createview inheritated from the generic views. However, there is also a way to implement this funcitonality within the generic createview. As for each form, it has a **form_valid()** function, we could override this function, with a judgement when it is a past date input, it will return the **form_invalid()**, which will return a ***message.error*** and provide to the user for the invalidation.
```python
    def form_valid(self, form):
        form.instance.owner = self.request.user
        if form.instance.arrival_date < timezone.now():
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)
```
5. For the reason that, each ride has its own status, we need to perform different actions based on different status, there is a feasible way is that using the **filter()**, but we have to specify three filters everytime, which is a voliation of the program design rule "Don't repeat yourself". I chose a more convinient way, which is to include a ***@property definition*** in the model, this could be directly called, when we need to perform judgement, we don't have to use the filter(), neither the equalizaiton judgement.
6. For the Ride owner to delete their ride, and enable the functionality to only delete their own ride in **generic.DeleteView**, we need to include an extra function in it.
```python
def test_func(self):
        ride_owner = self.get_object()
        if self.request.user == ride_owner.owner:
            return True
        return False
```
***
## ***Driver***:
1. For the driver class, this is included in the Ride class as mentioned before, as a ***ForeignKey***, this means that this driver can be exist for this ride (*Confirmed status*), or it doesn't exist (*Open ride*). In addition, the user could be registered as a Driver or not. This will cause a problem, if we use ***get_object_404***, as this will cause a 404 warning in the website, which we don't want. Instead, we need to user **fitler()** to obtain the queryset. I made a mistake by accessing the object using the **[index]**, as this will fail when there is no object in the queryset. The right option is using the **first()** function to automatically find the object.
```python
drive_info = Driver.objects.filter(user=request.user).first()
```
2. As mentioned before, in most cases **get_object_404** is a greate function call, to find the specific instance using the parameter passed in, usually self-generated id for the objects. However, there is a point need to be careful, when we try to present this id in the url, we have to correctly specify the type of the id, sometimes it is just the self-generated int value, but we also use the unique id for the Ride to make it more close to the reality. 
3. For the driver search view, we need to select the ride matching with the driver to present to the driver. Here, we need a filter that performs a **OR** operation, however, the **filter()** itself won't achieve that. Instead a ***Q*** function is called to perform the OR operation. The optional request matching problems have been discussed in the ride section.
4. For the driver, they have the ability to confirm the ride, which will send the emails to the owner and sharer(*if exist*), however, to support this we need to include our email which regards as the sender in the setting.py and views.py. This may cause some **security problem**, so instead of using outlook which will store the password in cleartext, I used 163 email, which will help to generate a authenticated code to support sending email. 
***
## ***Sharer***
This Sharer is not the same as Driver, but it is like another ride request from the user end, but it also should associate with the Ride. As a Ride should be able to have more than one sharers, it is easily to come up with the idea of setting a **ManyToManyField** in the Ride class. However, this may make the sharer infomation find, and the relation between the sharer and ride very difficult. Reversely, we choose to have a **ForeignKey**, that is a Ride. Furthermore, one sharer request will only associate with one ride, and the object will only be created when it is associated with a ride. This could further optimize our sharer fields, to exclude the arrival date and destination, but only need to have the sharer's party number. 
1. For the form of inquring the sharer information, it will ask the earliest time and latest time. Logically, the latest time should be no later than the earliles time and neither of them should be earlier than today. This is achieved by overriding the **clean_data** in the forms. 
```python
    def clean_earliest_time(self):
        data = self.cleaned_data['earliest_time']
        if data < timezone.now():
            raise ValidationError(_('Invalid date - search for past'))
        self.temp = data
        return data
```
2. For the sharer search, not only the asked inputs should be checked, but also the number should be checked, as defined in our system, the vehicles' maximum capacity is 6 (*Customers only*).
3. Sharer should declare the Ride ForeignKey, ***on_delete*** property as **CASCADE**, otherwise, if we delete the ride, the sharer objects will stay in our database as a piece of junk data.
4. As sharers will have a number which should be added to the ride total number, and this number should also be needed to delete when the sharer leaves the ride, otherwise, we may have a negative number, or the total number goes up unlimitedly.
***
## ***General Problem***
Below are some bugs or problems that are countered in many situations:
1. For the html file, if we need to include some variables passed through the view context, there is no syntax checking, it is easy to have some type in the name, which will result in a error or just not showing anything. As a result, a clear check is needed in the variable name. 
2. Still in the html file, if we want to use some for or if conditional sentences, we need to have a **"{% %}"**, however, it is easily to have a blank space between the "{" and "%", which will result in a invalid sentence, but directly show in text form. 
3. For the DeleteView, a success url should be explicit declare, however, if we just have a string here, it will replace the "delete" string, and replace with the declared one. However, this will lead to a empty url, as the ride_id is declared in the url, and it is gone for now. Instead, we need to use a ***reverse_lazy()*** to navigate using the name.
```python
success_url = reverse_lazy('rides')
```