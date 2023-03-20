from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("list/<str:listid>", views.list, name="list"),
    path("watch", views.watch, name="watch"),
    path("removefromwatch", views.removefromwatch, name="removefromwatch"),
    path("bidding", views.bidding, name="bidding"),
    path("commenting", views.commenting, name="commenting"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),

]
