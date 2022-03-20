from django.contrib import admin
# from .models import related models
from .models import CarMake
from .models import CarModel

# Register your models here.
admin.site.register(CarMake)
admin.site.register(CarModel)

# CarModelInline class
class CarModelInline(admin.ModelAdmin):
    fields = ['carMake', 'name', 'dealerId', 'type', 'year']

# Register your models here.

# CarModelInline class

# CarModelAdmin class

# CarMakeAdmin class with CarModelInline

# Register models here
