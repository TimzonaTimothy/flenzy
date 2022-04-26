from django.shortcuts import render
from store.models import ReviewRating
from store.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')[:8]

    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    context = {
        'products':products,
        'reviews':reviews,
    }
    return render(request, 'index.html', context)