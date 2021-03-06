from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting",views.create_listings,name="create"),
    path("<int:id>",views.listing,name="listing"),
    path("closebid/<int:id>",views.closebid,name="closebid"),
    path("categories",views.categories,name="categories"),
    path("category/<str:category>",views.category,name="category"),
    path("addcomment/<int:id>",views.addcomment,name="addcomment"),
    path("closedlisting", views.closedlisting, name="closedlisting"),
    path("toggle_watchlist/<int:id>", views.toggle_watchlist, name = "toggle_watchlist"),
    path("watchlist", views.watchlist, name = "watchlist"),
]
