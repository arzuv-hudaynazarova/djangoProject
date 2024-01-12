from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Order, OrderItem, ShippingAddress
from .forms import CustomUserCreationForm
from .utils import cartData, guestOrder
import json
import datetime

# views.py


from django.http import JsonResponse


def apply_discount(request):
    data = json.loads(request.body)
    discount_code = data.get('discountCode', '')
    order_id = data.get('orderId')  # You need to send this from the frontend as well

    try:
        order = Order.objects.get(id=order_id, complete=False)
        if discount_code.lower() == 'hedef':
            discount_percent = 25
            discount_amount = order.get_cart_total * (discount_percent / 100)
            order.discount_total = order.get_cart_total - discount_amount
            order.save()
            return JsonResponse({'success': True, 'new_total': order.discount_total})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid discount code'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})


# CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'age', 'is_staff']


# Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})


# Category List View
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


# Product List View
def product_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/product_list.html', {'category': category, 'products': products})


# Main Store View
def store(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        category = None
        products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/store.html', {'categories': categories, 'category': category, 'products': products})


# Custom Login View
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    extra_context = {'page_title': 'Login to Your Account'}


# Search Results View
def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'store/search.html', {'products': products})


# Cart View
def cart(request):
    data = cartData(request)
    return render(request, 'store/cart.html', data)


# Checkout View
def checkout(request):
    data = cartData(request)
    return render(request, 'store/checkout.html', data)


# Update Item View
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# Process Order View
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total():
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
