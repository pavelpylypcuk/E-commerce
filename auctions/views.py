from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.db import models
from decimal import Decimal
from django.db.models import Max

from .models import User, Auction_listing, Auction_listingForm, Bid, Comment, CommentForm, Watchlist

def index(request):
    """ Shows all active listings. """ 
    
    # finds a current bid for each listing via a SQL query
    current_bid = Auction_listing.objects.annotate(max_bid=Max('bid__bid'))
        
    return render(request, "auctions/index.html", { 
        "auctions": Auction_listing.objects.filter(active=True),
        "current_bid": current_bid
    })


def login_view(request):
    """ Logs in user. """
    
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """ Logs out current user. """
    
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """ Registers a new user. """
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    """ Creates and saves new auction listings """
    
    # if data is submitted
    if request.method == 'POST':
        # populate a form variable with user data
        form = Auction_listingForm(request.POST)
        
        # make sure form is valid and that user provides a minimum required price
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.price >= 0.01:
                instance.user = request.user
                instance.save()
                return HttpResponseRedirect(reverse("index"))
            # return an error message if user tries to bypass HTML verification
            else:
                return render(request, 'auctions/apology.html', {
                    'message': "Looks you tried to bypass the HTML verification. Unfortunately, your hacker level is too low to break this site."
                })
        # return error message if form is not valid
        else:
           return render(request, 'auctions/apology.html', {
                    'message': "Form is invalid."
                }) 
    # if reached via URL
    else:
        form = Auction_listingForm()
    
    return render(request, 'auctions/create_listing.html', {'form': form})

def current_listing(request, auction_id):
    """ Renders a selected auction listing. """
    
    # if user is not logged in, display an error message
    if not request.user.is_authenticated:
        return render(request, 'auctions/apology.html', {
            'message': "You must be logged in to see this listing."
        })
        
    else:
        # query for watchlist status of the selected listing
        watchlist_item = Watchlist.objects.filter(user = request.user, auction_listing_id = auction_id)
        # query for the selected listing's data in the database
        listing = Auction_listing.objects.get(pk = auction_id)
        # if data is submitted
        if request.method == 'POST':
            # if user submits form via the watchlist button
            if request.POST.get('Watchlist_delete') or request.POST.get('Watchlist_add'):
                # check whether listing is on watchlist, if not add it, if yes remove it from watchlist
                if watchlist_item:
                    watchlist_item.delete()
                else:
                    watchlist = Watchlist(user = request.user, auction_listing_id = auction_id)
                    watchlist.save()
            # if user submits form via the place bid button
            elif request.POST.get('min_bid') or request.POST.get('min_price'):
                # if previous bids were already made
                if request.POST.get('min_bid'):
                    # if user provided amount is greater than the current highest bid
                    if Decimal(request.POST.get('min_bid')) > Bid.objects.filter(auction_listing_id = auction_id).aggregate(Max('bid')).get('bid__max'):
                        bid = Bid(user = request.user, auction_listing_id = auction_id, bid = request.POST.get('min_bid'))
                        bid.save()
                    # return an error message if user tries to bypass HTML verification
                    else:
                        return render(request, 'auctions/apology.html', {
                    'message': "Looks you tried to bypass the HTML verification. Unfortunately, your hacker level is too low to break this site."
                })
                # if no bids were made yet 
                elif request.POST.get('min_price'):
                    # if user provided amount is greater than or equal to the starting price
                    if Decimal(request.POST.get('min_price')) >= listing.price:
                        bid = Bid(user = request.user, auction_listing_id = auction_id, bid = request.POST.get('min_price'))
                        bid.save()
                    # return an error message if user tries to bypass HTML verification
                    else:
                        return render(request, 'auctions/apology.html', {
                    'message': "Looks you tried to bypass the HTML verification. Unfortunately, your hacker level is too low to break this site."
                })
            # if user submits form via the post comment button 
            elif request.POST.get('post'):
                form = CommentForm(request.POST)
                # verify form is valid
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.user = request.user
                    instance.auction_listing_id = auction_id
                    instance.save()
                # else return an error message
                else:
                    return render(request, 'auctions/apology.html', {
                    'message': "Form is invalid."
                })
            # if user submits form via the close auction button
            elif request.POST.get('close'):
                listing.active = False
                listing.save()
                    
            return HttpResponseRedirect(reverse("current_listing", kwargs={'auction_id': auction_id }))
        
        # if reached via URL
        else:
            form = CommentForm()
            # check if bid exists for current auction listing
            if Bid.objects.filter(auction_listing_id = auction_id).aggregate(Max('bid')).get('bid__max'):
                # query for the current bid in current listing
                current_bid = round((Bid.objects.filter(auction_listing_id = auction_id).aggregate(Max('bid')).get('bid__max')), 2)
                # find the user who made the current bid
                max_price = Bid.objects.get(auction_listing_id = auction_id, bid = Bid.objects.filter(auction_listing_id = auction_id).aggregate(Max('bid')).get('bid__max'))
                winner = max_price.user
            # if not bids were made, initiliaze both variables to 0 
            else:
                current_bid = 0
                winner = 0
            return render(request, 'auctions/current_listing.html', {
                'listing': listing,
                'price': listing.price,
                'watchlist': watchlist_item,
                "bid_count": Bid.objects.filter(auction_listing_id = auction_id).count(),
                "min_bid": current_bid + Decimal(0.01),
                "current_bid": current_bid,
                "winner": winner,
                "form": form,
                "comments": Comment.objects.filter(auction_listing_id = auction_id),
                "user": request.user
            })

@login_required    
def watchlist(request):
    """ Renders all listing in current user's watchlist. """
    
    # query for listings that are in current user's watchlist
    auctions = Auction_listing.objects.filter(watchlist__user=request.user)
    current_bid = Auction_listing.objects.annotate(max_bid=Max('bid__bid'))
            
    return render(request, 'auctions/watchlist.html', {
        'auctions': auctions,
        "current_bid": current_bid
    })
    
def categories(request):
    """ Render available categories of all active listings. """
    
    # query for all active listings and initialize an empty list
    listing = Auction_listing.objects.filter(active=True)
    categories = []
    # loop over all listings, if category of current listing is not yet present in the categories list, add it there
    for lis in listing:
        if lis.category not in categories and lis.category != '':
            categories.append(lis.category)
    
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })
    
def category(request, category):
    """ Render all active listings in selected category. """
    
    # query for all active listings in selected category
    auctions = Auction_listing.objects.filter(category=category, active=True)
    current_bid = Auction_listing.objects.annotate(max_bid=Max('bid__bid'))
    
    return render(request, 'auctions/category.html', {
        'auctions': auctions,
        'category': category,
        "current_bid": current_bid
    })