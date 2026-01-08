from django.shortcuts import render, get_object_or_404
from rest_framework import status
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db import transaction
import requests
from .serializers import ProductInfoSerializer, ProductTradeSerializer
from .models import Product
from .capabilities import DESCRIPTION_MAP

HUB_URL = settings.HUB_URL
MY_IP = settings.MY_IP

# falta padronizar respostas
# após finalizar todos os endpoints (com edge cases satisfeitos)
# criar ServiceLayer em cima do resultado final
# fazer testes em cima do ServiceLayer/Endpoints

class ProductCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductInfoSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "status": "success",
                "id": product.id,
                "created": product.created,
                "product": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "action": "creation"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductChangeInfo(APIView):
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('product')
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductInfoSerializer(product, data=request.data, partial=True)


        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "status": "success",
                "id": product.id,
                "modified": product.modified,
                "product": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "action": "update"
            })
        else:
            return Response({
                "status": "error",
                "message": serializer.errors,
                "action": "update"
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductFindAPIView(APIView):
    def get(self, request, *args, **kwargs):
        product = kwargs.get('product')

        if product:
            query = Product.objects.get(slug=product)
            serializer = ProductInfoSerializer(query)
        else:
            query = Product.objects.all()
            serializer = ProductInfoSerializer(query, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductBuyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('product')
        quantity = int(kwargs.get('quantity'))

        product, created = Product.objects.get_or_create(
            name=product_slug,
            defaults={
                "name": product_slug,
                "quantity": quantity,
                "price": 0,
                "is_active": False,
            },
        )

        if created:
            product.save()
            return Response({
                "status": "success",
                "id": product.id,
                "created": product.created,
                "product": product.name,
                "quantity": product.quantity,
                "message": "New product added to the database!",
                "warning": f"UPDATE THE INFO OF THE NEW PRODUCT HERE: {product.get_absolute_url()}",
                "action": "creation",
            }, status=status.HTTP_201_CREATED)
        else:
            product.quantity += quantity
            product.save()

            return Response({
                "status": "success",
                "product": product.name,
                "quantity": product.quantity,
                "action": "bought",
            }, status=status.HTTP_200_OK)


class ProductSellAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data['quantity']
        product = Product.objects.get(slug=data['product'])
        _transaction = True

        if product.quantity < quantity:
            quantity_needed = quantity - product.quantity
            _transaction = False
            # request supliers from HUB endpoint.
            _hub_request_data = {
                "product": product.slug,
                "quantity": quantity_needed,
                "ip": MY_IP
            }

            _hub_request_endpoint = f"{HUB_URL}/hub/v1/request/"
            
            hub_response = requests.post(
                url=_hub_request_endpoint,
                json=_hub_request_data,
                timeout=(1, 3)
            )

            hub_response.raise_for_status()
            
            if hub_response.status_code != 200:
                return Response({
                    "status": "error",
                    "message": "operation failed due to HubAPIService."
                }, status=status.HTTP_200_OK)
            
            # working with supliers found on response
            data = hub_response.json()

            for suplier in data["supliers"].values():
                print(suplier)
                _suplier_trade_endpoint = f"http://{suplier["ip"]}/cd/v1/product/sell/"
                _suplier_data = {
                    "product": product.slug,
                    "quantity": quantity_needed
                }

                _suplier_response = requests.post(
                    url=_suplier_trade_endpoint,
                    json=_suplier_data,
                    timeout=(1, 3)
                )

                if _suplier_response.status_code == 200:
                    _transaction = True
                    product.quantity += quantity_needed
                    product.save()
                else:
                    continue
        
        if _transaction:
            product.quantity -= quantity
            product.save()

            return Response({
                "status": "success",
                "product": product.slug,
                "quantity_sold": quantity,
                "total_price": product.price * quantity,
                "operation_result": _transaction,
                "operation": "transaction"
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "success",
            "operation_result": _transaction,
            "message": "could not find supliers for trade request.",
            "product": product.slug,
            "quantity_requested": quantity,
            "available_quantity": product.quantity
        }, status=status.HTTP_200_OK)


class HubTradeResponseAPIView(APIView):
    """
    POST - **product** and **quantity**
    - HUB will access this endpoint to gather the candidates to trade
    - *WARNING: Apply permissions rules to this endpoint (only HUB can access)*
    """
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('product')
        quantity = int(kwargs.get('quantity'))
        
        product = get_object_or_404(Product, slug=product_slug)

        if product.quantity >= quantity:
            available = True
        else:
            available = False

        return Response({
            "status": "success",
            "id": product.id,
            "total_price": product.price * quantity,
            "available": available,
            "ip": MY_IP,
            "action": "report"        
        }, status=status.HTTP_200_OK)


class DescriptionListView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({
            "service": "cd",
            "version": "1.0",
            "actions": DESCRIPTION_MAP
        }, status=status.HTTP_200_OK)
