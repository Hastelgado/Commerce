from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class listings(models.Model):
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=200)
    price = models.IntegerField()
    category = models.CharField(max_length=50)
    imageurl = models.URLField(blank=True)
    activity = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userlistings")

    def __str__(self):
        return f"{self.id}: Title: {self.title}, price: {self.price}, Belongs to: {self.user.username}, {self.activity}"


class bid(models.Model):
    amount = models.IntegerField()
    listing = models.ForeignKey(listings,on_delete=models.CASCADE,related_name="bidlistings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userbids")

    def __str__(self):
        return f"{self.id}: {self.user.username} bid '{self.amount}' on {self.listing.title}"


class comment(models.Model):
    text = models.CharField(max_length=500)
    listing = models.ForeignKey(listings,on_delete=models.CASCADE,related_name="commentlistings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments")

    def __str__(self):
        return f"{self.id}: {self.user.username} commented '{self.text}' on {self.listing.title}"


class watchlist(models.Model):
    listing = models.ManyToManyField(listings,related_name="watchlists", blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userwatchlist")

    def __str__(self):
        return f"{self.id}: Listings: {self.listing}, Belongs to: {self.user.username}"
