from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User
from .models import  Listing,Bid,Comments,Winner,Watchlist
from django.contrib.auth.decorators import login_required
from annoying.functions import get_object_or_None


def index(request):
    # list of products available
    products = Listing.objects.all()
    empty = False
    # checking if there are any products
    if len(products) == 0:
        empty = True
    return render(request, "auctions/index.html", {
        "products": products,
        "empty": empty})


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
@login_required(login_url='/login')
def create_listings(request):
    #if post method
    if request.method=="POST":
        #new object 
        product=Listing()
        #getting each field from the form
        product.seller=request.user.username
        product.Name=request.POST.get('Name')
        product.current_bid=request.POST.get('starting_bid')
        product.description=request.POST.get('description')
        product.category=request.POST.get('category')
        if request.POST.get('image_link'):
            product.image_link=request.POST.get('image_link')
        else:
            product.image_link="https://www.sandu.in/image/cache/catalog/product/no-product-800x800.png"
        #save data in database
        product.save()
        #all the objects in listings
        products=Listing.objects.all()
        empty=False
        if len(products)==0:
            empty = True

        return render(request,"auctions/index.html",{"products": products,
        "empty": empty})
    #if not npost then redirect to createlisting page
    else:
        return render(request, "auctions/createlisting.html")
#individual listing page
@login_required(login_url='/login')
def listing(request,id):
    #get item based on id
    item=Listing.objects.get(id=id)
    comments=Comments.objects.filter(listingid=id)
    #if bid placed
    if request.method=="POST":
        new_bid=int(request.POST.get('newbid'))
        #check starting one is greater than or equal to bid, object item will have attributes
        if item.current_bid>=new_bid:
            return render(request,"auctions/listing.html",{"msg":"Your bid must be higher than current bid" ,"item":item,"comments":comments,"msg_type":"danger"})
        else:
            item.current_bid=new_bid
            item.save()
            bobj=Bid.objects.filter(listingid=id)
            #if a bid already exists then delete
            if bobj:
                bobj.delete()
            #save 
            bobj=Bid()
            bobj.user=request.user
            bobj.title=item.Name
            bobj.bid=new_bid
            bobj.listingid=id
            bobj.save()
            
            
            return render(request,"auctions/listing.html",{"msg":"Your bid has been successfully placed" ,"item":item,"comments":comments})
    else:
        obj = Listing.objects.filter(id = id).first()
        there = Watchlist.objects.filter(user = request.user, listing = obj).first()
        return render(request,"auctions/listing.html",{"item":item,"comments":comments, "there":there})
#when seller clicks on closebid button
@login_required(login_url='/login')
def closebid(request,id):
    winobj = Winner()
    listobj = Listing.objects.get(id=id)
    obj = get_object_or_None(Bid, listingid=id)
    if not obj:
        message = "Deleting Bid"
        msg_type = "danger"
    else:
        bobj = Bid.objects.get(listingid=id)
        winobj.owner = request.user.username
        winobj.winner = bobj.user
        winobj.productid = id
        winobj.winning_cost = bobj.bid
        winobj.name = bobj.title
        winobj.save()
        message = "Bid Closed"
        msg_type = "success"
        # deleting from Bid
        bobj.delete()
    # removing from Comment
    if Comments.objects.filter(listingid=id):
        commentobj = Comments.objects.filter(listingid=id)
        commentobj.delete()
    
    # removing from Listing
    listobj.delete()
    # retrieving the new products list after adding and displaying
    # list of products available in WinnerModel
    winners = Winner.objects.all()
    # checking if there are any products
    empty = False
    if len(winners) == 0:
        empty = True
    return render(request, "auctions/closedlisting.html", {
        "products": winners,
        "empty": empty,
        "message": message,
        "msg_type": msg_type
    })
#to see closed listings
@login_required(login_url='/login')
def closedlisting(request):
    # list of products available in WinnerModel
    winners = Winner.objects.all()
    # checking if there are any products
    empty = False
    if len(winners) == 0:
        empty = True
    return render(request, "auctions/closedlisting.html", {
        "products": winners,
        "empty": empty
    })

def categories(request):
    return render(request,"auctions/categories.html")
def category(request,category):
    #retrieving objects in listing of the category:category 
    category_objs=Listing.objects.filter(category=category)
    if category_objs:

        return render(request,"auctions/category.html",{"category":category,"products":category_objs})
    else:
        return render(request,"auctions/category.html",{"category":category,"products":category_objs,"msg":"No active listings in this category"})
#view to process form and add comment to database
@login_required(login_url='/login')
def addcomment(request,id):
    #create comment object
    new_comment=Comments()
    new_comment.comment=request.POST.get('comment')
    new_comment.listingid=id
    new_comment.user=request.user.username
    new_comment.save()
    item=Listing.objects.get(id=id)
    comments=Comments.objects.filter(listingid=id)
    obj = Listing.objects.filter(id = id).first()
    there = Watchlist.objects.filter(user = request.user, listing = obj).first()
    return render(request,"auctions/listing.html",{"item":item,"comments":comments,"there":there})


def toggle_watchlist(request, id):
    #first returns first object or None
    obj = Listing.objects.filter(id = id).first()
    w = Watchlist.objects.filter(user = request.user, listing = obj).first()
    item=Listing.objects.get(id=id)
    comments=Comments.objects.filter(listingid=id)
    #check if item there in watchlist
    #if not there
    if w is None:
        wl = Watchlist.objects.create(user = request.user,listing = obj)
        wl.save()
        there = Watchlist.objects.filter(user = request.user, listing = obj).first()
        return render(request,"auctions/listing.html",{"item":item,"comments":comments,"there":there})
    #if there
    w.delete()
    there = Watchlist.objects.filter(user = request.user, listing = obj).first()
    return render(request,"auctions/listing.html",{"item":item,"comments":comments,"there":there})
    
@login_required
def watchlist(request):
    wl = Watchlist.objects.filter(user =request.user)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": wl
    })
