from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
        product = get_object_or_404(slug=slug)
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
            slug=data["product"],
            defaults={
                "name": data.get("name", data["product"]),
                "quantity": data.get("quantity", 0),
                "price": data.get("price", 0),
                "is_active": False,
            },
        )

        if created:
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
            product.quantity += data["quantity"]
            product.save()

            return Response({
                "status": "success",
                "product": product.name,
                "quantity": product.quantity,
                "action": "bought",
            }, status=status.HTTP_200_OK)