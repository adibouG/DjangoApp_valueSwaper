from django.contrib import admin

from .models import Bike, CoreModule, BikeIdSwap, Swaper
# Register your models here.
admin.site.register (Bike)
admin.site.register (CoreModule)
admin.site.register (BikeIdSwap)
admin.site.register (Swaper)