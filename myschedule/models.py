from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    """
        Stores the user's saved carts. Sections is a url parameter containing
        the sections for the cart.
    """

    owner = models.ForeignKey(User, blank=True, null=True)
    description = models.CharField(max_length=50,
                help_text='Brief description that identifies this schedule.')
    sections = models.CharField(max_length=300)
    def __unicode__(self):
        return self.description

#TODO: Get rid of cartitem when we're sure we're going with storing the sections url.
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

