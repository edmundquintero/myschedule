from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    """
        Parent for cart items.  Will only have an owner if the user logs in to
        the application.
    """
    # TODO: consider using email address instead of foreignkey relationship for
    # owner if want to tie a cart to someone without a cpcc account.
    owner = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.id

class CartItem(models.Model):
    """
        Contains the items (course sections) a user adds to their cart.
        Date added will be used by a cron job to remove outdated items
        (when all items are removed from a cart, the cart record will
        need to be removed as well).
    """
    cart = models.ForeignKey(Cart)
    section = models.CharField(max_length=25)
    date_added = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.section

