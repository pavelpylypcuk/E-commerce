from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.forms import ModelForm
from django.http import HttpRequest
from django import forms

class User(AbstractUser):
    pass

class Auction_listing(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    description = models.CharField(max_length=150)
    url = models.URLField(default=None, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Bid(models.Model):
    auction_listing = models.ForeignKey(Auction_listing, on_delete=models.CASCADE)
    name = "Bid"
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        name = f"{self.user}/{self.auction_listing}"
        return name
    
class Comment(models.Model):
    comment = models.CharField(max_length=250, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    auction_listing = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, default=None, blank=True)

    def __str__(self):
        name = f"{self.user}/{self.auction_listing}"
        return name
    
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    auction_listing = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, default=None)
    
    def __str__(self):
        name = f"{self.user}/{self.auction_listing}"
        return name
    
class Auction_listingForm(ModelForm):
    class Meta:
        model = Auction_listing
        exclude = ['active'] 
        widgets = {'user': forms.HiddenInput(),
                   'price': forms.NumberInput(attrs={'min': 0.01})}
        
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['name']
        widgets = {'user': forms.HiddenInput(),
                   'auction_listing': forms.HiddenInput(),
                   'comment': forms.Textarea}
        labels = {
            'comment': ""
        }