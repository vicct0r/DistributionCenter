from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db import transaction

import requests
from .serializers import ProductInfoSerializer, ProductTradeSerializer
from .models import Product


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
    def patch(self, request, *args, **kwargs):
        serializer = ProductTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product, created = Product.objects.get_or_create(
            name=data["product"],
            defaults={
                "name": data.get("name", data["product"]), # preciso fazer com que o valor de entrada seja um slug
                "quantity": data.get("quantity", 0),
                "price": data.get("price", 0),
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
                "warning": f"UPDATE THE INFO OF THE NEW PRODUCT HERE: /product/info/{product.slug}/",
                "action": "creation",
            }, status=status.HTTP_201_CREATED)

        else:
            product.quantity += data["quantity"]
            product.save()

            return Response({
                "status": "success",
                "product": product.name,
                "quantity": product.quantity,
                "action": "bought",
            }, status=status.HTTP_200_OK)

 
class ProductSellAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product_slug = data['product']
        quantity = data['quantity']

        product = get_object_or_404(Product, slug=product_slug)
        
        if product.quantity < quantity:
            hub_ip = settings.HUB_IP
            quantity_needed = quantity - product.quantity

            request_json = {
                "product": product.slug,
                "quantity": quantity_needed
            }

            try:
                response = requests.post(
                    url=f"http://{hub_ip}/hub/v1/request/",
                    json=request_json,
                    timeout=5
                )

                response.raise_for_status()
            except Exception as e:
                print("Erro capturado no endpoint ProductSellAPIView: " + str(e))
                return Response({
                    "status": "error",
                    "message": "Failed to communicate with the HUB!",
                    "error_msg": str(e)
                }, status=status.HTTP_424_FAILED_DEPENDENCY)

            if response.status_code != 200: # Pensar em como tratar isso de forma correta
                return Response({
                    "status": "error",
                    "message": "HUB could not answer correctly."
                }, status=status.HTTP_200_OK) # Não esta OK, mas preciso saber se a response influencia no fluxo
            
        with transaction.atomic():
            product.quantity -= quantity
            product.save()

            return Response({
                "status": "success",
                "message": f"Sold {quantity_needed} units of {product.slug}.",
                "product": product.name,
                "quantity": product.quantity, 
                "action": "transaction"
            }, status=status.HTTP_200_OK)


class HubTradeResponseAPIView(APIView):
    """
    POST - **product** and **quantity**
    - HUB will access this endpoint to gather the candidates to trade
    - *WARNING: Apply permissions rules to this endpoint (only HUB can access)*
    """
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        quantity = int(kwargs.get('quantity'))

        product = get_object_or_404(Product, slug=product_slug)

        if product.quantity <= quantity:
            available = True
        else:
            available = False

        return Response({
            "status": "success",
            "product": product.slug,
            "quantity": product.quantity,
            "price": product.price,
            "available": available,
            "action": "report"        
        }, status=status.HTTP_200_OK)