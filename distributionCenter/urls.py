from django.urls import path
from . import views


urlpatterns = [
    path('product/create/', views.ProductCreateAPIView.as_view(), name='product_create'),
    path('product/update/<slug:product>/', views.ProductChangeInfo.as_view(), name='product_update'),
    path('product/info/', views.ProductFindAPIView.as_view(), name='product_list'),
    path('product/info/<slug:product>/', views.ProductFindAPIView.as_view(), name='product_detail'),
    path('product/buy/', views.ProductBuyAPIView.as_view(), name='product_buy')
]