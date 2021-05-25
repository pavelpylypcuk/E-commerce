from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Auction_listing, Bid, Comment, Watchlist

# Register your models here.

admin.site.register(Auction_listing)
admin.site.register(Bid)
admin.site.register(User, UserAdmin)
admin.site.register(Watchlist)
admin.site.register(Comment)