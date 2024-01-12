from django.urls import path
from . import views
from .views import LoginView
from .views import CustomLoginView

from .views import store
from .views import register
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('search/', views.search_results, name='search_results'),
    path('login/', LoginView.as_view(), name='login'),
    path('categories/', views.category_list, name='category_list'),  # Path to view all categories
    path('categories/<int:category_id>/', views.product_list, name='product_list'),
    path('', store, name='store'),  # The main page showing all categories
    path('category/<int:category_id>/', store, name='store'),
    path('register/', register, name='register'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
