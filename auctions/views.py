from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import *

catlist = ["fashion","toys","electronics","home"]

def index(request):
    lists = listings.objects.all()
    
    return render(request, "auctions/index.html",{
        "lists":lists,
    })


def login_view(request):
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
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
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


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        price = request.POST.get("price")
        category = request.POST.get("category")
        imageurl = request.POST.get("imageurl")
        desc = request.POST.get("desc")
        currentuser = User.objects.get(id=request.user.id)

        newlist = listings(title=title, price=price, category=category, imageurl=imageurl, desc=desc, user=currentuser)
        newlist.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html",{
            "catlist":catlist,
        })


@login_required(login_url='login')
def list(request, listid):
    list = listings.objects.get(id=listid)
    currentuser = User.objects.get(pk=request.user.id)
    allbids = list.bidlistings.all()
    allcomments = list.commentlistings.all()

    bidlist = []
    for b in allbids:
        bidlist.append(b.amount)

    if bidlist:
        max_bid = int(max(bidlist))
    else:
        max_bid = 0
        
    winningbid = bid.objects.filter(amount=max_bid).first()

    if watchlist.objects.filter(user=currentuser).exists():
        wlist = watchlist.objects.get(user=currentuser)
        if wlist.listing.filter(pk=listid).exists():
            item = "exists!"
            return render(request, "auctions/list.html", {
            "list":list, "item":item, "bids":allbids, "username": currentuser.username, "winningbid": winningbid, "comments": allcomments,
            })
        else:
            return render(request, "auctions/list.html", {
            "list":list, "bids":allbids, "username": currentuser.username, "winningbid": winningbid, "comments": allcomments,
            })
    else:
        return render(request, "auctions/list.html", {
            "list":list, "bids":allbids, "username": currentuser.username, "winningbid": winningbid, "comments": allcomments,
        })



def watch(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            id = request.POST.get("listid")
            userid = request.user.id
            l = listings.objects.get(pk=id)
            currentuser = User.objects.get(pk=request.user.id)

            if watchlist.objects.filter(user=currentuser).exists():
                wlist = watchlist.objects.get(user=currentuser)
                wlist.listing.add(l)
                return HttpResponseRedirect(reverse("watch"))
            else:
                new_wlist = watchlist.objects.create(user=currentuser)
                new_wlist.listing.add(l)
                wlist = watchlist.objects.get(user=currentuser)
                wlist = wlist.listing.all()
                return render(request, "auctions/watchlist.html",{
                "watchlist": wlist, "username": currentuser.username,
            })

        else:
            currentuser = User.objects.get(pk=request.user.id)
            if watchlist.objects.filter(user=currentuser).exists():
                wlist = watchlist.objects.get(user=currentuser)
                wlist = wlist.listing.all()
                return render(request, "auctions/watchlist.html",{
                    "watchlist": wlist, "username": currentuser.username,
                })
            else:
                return render(request, "auctions/watchlist.html",{
                    "username": currentuser.username,
                })
    else:
        return render (request, "auctions/login.html")


@login_required(login_url='login')
def removefromwatch(request):
    id = request.POST.get("listid")
    l = listings.objects.get(pk=id)
    currentuser = User.objects.get(pk=request.user.id)
    wlist = watchlist.objects.get(user=currentuser)
    wlist.listing.remove(l)
    return HttpResponseRedirect(reverse("watch"))
        

@login_required(login_url='login')
def bidding(request):
    if (request.POST.get("placebid")):

        id = request.POST.get("listid")
        amount = int(request.POST.get("bidamount"))
        currentuser = User.objects.get(pk=request.user.id)
        l = listings.objects.get(pk=id)

        if bid.objects.filter(user=currentuser, listing=l).exists():
            return render (request, "auctions/error.html",{
                "errormessage":"You've already bid on this list before!"
            })
        
        startingbid = int(l.price)
        allbids = l.bidlistings.all()
        list = []
        for b in allbids:
            list.append(b.amount)

        if list:
            max_bid = int(max(list))
        else:
            max_bid = 0

        if amount>=startingbid and amount>max_bid:    
            new_bid = bid(amount=amount, listing=l, user=currentuser)
            new_bid.save()
            return HttpResponseRedirect(reverse("list", kwargs={"listid":id}))
        else:
            return render (request, "auctions/error.html",{
                "errormessage":"Your bid must higher than the highest bid currently.(or equal to starting bid)"
            })
    elif (request.POST.get("deletebid")):

        id = request.POST.get("listid")
        currentuser = User.objects.get(pk=request.user.id)
        l = listings.objects.get(pk=id)
        b = bid.objects.get(user=currentuser, listing=l)
        b.delete()
        return HttpResponseRedirect(reverse("list", kwargs={"listid":id}))
    
    elif (request.POST.get("closebid")):

        id = request.POST.get("listid")
        currentuser = User.objects.get(pk=request.user.id)
        l = listings.objects.get(pk=id)
        l.activity=False
        l.save()

        return HttpResponseRedirect(reverse("list", kwargs={"listid":id}))


def commenting(request):

    id = request.POST.get("listid")
    text = request.POST.get("commentarea")
    currentuser = User.objects.get(pk=request.user.id)
    l = listings.objects.get(pk=id)

    if (request.POST.get("addcomment")):

        new_comment = comment(text=text, listing=l, user=currentuser)
        new_comment.save()
        return HttpResponseRedirect(reverse("list", kwargs={"listid":id}))
    
    if (request.POST.get("deletecomment")):

        commentid = request.POST.get("commentid")
        c = comment.objects.get(pk=commentid)
        c.delete()
        return HttpResponseRedirect(reverse("list", kwargs={"listid":id}))


def categories(request):

    return render (request, "auctions/categories.html",{
                "categories":catlist,
            })


def category(request, category):

    filtered_listings = listings.objects.filter(category=category)

    return render (request, "auctions/category.html",{
                "listings":filtered_listings, "category":category,
            })