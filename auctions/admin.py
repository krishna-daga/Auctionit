from django.contrib import admin
from .models import Listing,Bid,Comments,Winner,Watchlist

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comments)
admin.site.register(Winner)
admin.site.register(Watchlist)

