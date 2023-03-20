from django.contrib import admin
from auctions.models import *

# Register your models here.

admin.site.register(User)
admin.site.register(listings)
admin.site.register(bid)
admin.site.register(comment)
admin.site.register(watchlist)