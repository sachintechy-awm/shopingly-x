from .cart import Cart
from .models import Category


def cart(request):
    return {'cart': Cart(request)}


def categories(request):
    return {'nav_categories': Category.objects.all()}
