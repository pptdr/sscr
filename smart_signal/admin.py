from django.contrib import admin
from .models import Client_details, videos_at, Client, signal_details,db_demo

# Register your models here.
admin.site.register(signal_details)
admin.site.register(db_demo)
admin.site.register(Client_details)
admin.site.register(videos_at)
admin.site.register(Client)
