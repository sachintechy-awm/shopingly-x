from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .ai_assistant import get_ai_recommendations
from .cart import Cart
from .models import Category, Order, OrderItem, Product


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:8]
    new_arrivals = Product.objects.order_by('-created_at')[:8]
    top_rated = Product.objects.order_by('-rating')[:8]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'top_rated': top_rated,
    })


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
        'total_results': paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1
    cart.add(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart), 'product_name': product.name})

    messages.success(request, f'"{product.name}" was added to your cart.')
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart)})

    messages.info(request, f'"{product.name}" was removed from your cart.')
    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity, update_quantity=True)

    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty — add something before checking out.")
        return redirect('store:product_list')

    if request.method == 'POST':
        required_fields = ['full_name', 'email', 'address', 'city', 'postal_code']
        if all(request.POST.get(field, '').strip() for field in required_fields):
            order = Order.objects.create(
                full_name=request.POST.get('full_name').strip(),
                email=request.POST.get('email').strip(),
                address=request.POST.get('address').strip(),
                city=request.POST.get('city').strip(),
                postal_code=request.POST.get('postal_code').strip(),
                phone=request.POST.get('phone', '').strip(),
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            return redirect('store:order_success', order_id=order.id)
        messages.error(request, "Please fill in all required fields.")

    return render(request, 'store/checkout.html', {'cart': cart})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})


@require_POST
def ai_search(request):
    query = request.POST.get('query', '').strip()
    if not query:
        return JsonResponse({'message': "Type what you're looking for and I'll help you find it.", 'products': []})

    products = Product.objects.select_related('category').all()
    result = get_ai_recommendations(query, products)
    return JsonResponse(result)


def signup(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to ShopinglyX!")
            return redirect('store:home')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Logged in successfully.")
            return redirect('store:home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('store:home')
