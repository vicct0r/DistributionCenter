from django.urls import path
from . import views


urlpatterns = [
    path('product/create/', views.ProductCreateAPIView.as_view()),
    path('info/', views.DescriptionListView.as_view()),
    path('product/update/<slug:product>/', views.ProductChangeInfo.as_view()),
    path('product/info/', views.ProductFindAPIView.as_view()),
    path('product/info/<slug:product>/', views.ProductFindAPIView.as_view()),
    path('product/buy/', views.ProductBuyAPIView.as_view()),
    path('product/sell/', views.ProductSellAPIView.as_view()),
    path('product/request/<slug:product>/<int:quantity>/', views.HubTradeResponseAPIView.as_view())
]