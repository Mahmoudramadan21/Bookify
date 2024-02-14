from django.shortcuts import render
import re

# rest-framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

# User model & serializers and models
from django.contrib.auth.models import User
from api.serializers import *
from api.models import *
# pagination
from django.core.paginator import Paginator, PageNotAnInteger, Page

# datetime
from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
#***************************************************************************#


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['paymentMethod', 'taxPrice', 'shippingPrice', 'totalPrice', 'shippingAddress', 'orderItems'],
    properties={
        'paymentMethod': openapi.Schema(type=openapi.TYPE_STRING),
        'taxPrice': openapi.Schema(type=openapi.TYPE_NUMBER),
        'shippingPrice': openapi.Schema(type=openapi.TYPE_NUMBER),
        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER),
        'shippingAddress': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'postalCode': openapi.Schema(type=openapi.TYPE_STRING),
                'country': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        'orderItems': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['book', 'qty', 'price'],
                properties={
                    'book': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'qty': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
    }
))
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    try:
        user = request.user
        data = request.data

        orderItems = data['orderItems']

        if orderItems and len(orderItems) == 0:
            return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
        else:

            # (1) Create order

            order = Order.objects.create(
                user=user,
                paymentMethod=data['paymentMethod'],
                taxPrice=data['taxPrice'],
                shippingPrice=data['shippingPrice'],
                totalPrice=data['totalPrice']
            )

            # (2) Create shipping address

            shipping = ShippingAddress.objects.create(
                order=order,
                address=data['shippingAddress']['address'],
                city=data['shippingAddress']['city'],
                postalCode=data['shippingAddress']['postalCode'],
                country=data['shippingAddress']['country'],
            )

            # (3) Create order items and set order to orderItem relationship
            for i in orderItems:
                book = Book.objects.get(id=i['book'])

                item = OrderItem.objects.create(
                    book=book,
                    order=order,
                    name=book.name,
                    qty=i['qty'],
                    price=i['price'],
                    image=book.image.url,
                )

                # (4) Update stock

                book.countInStock -= item.qty
                book.save()

            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    try:
        user = request.user
        orders = user.order_set.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except:
        return Response('Unexpected error')

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    except:
        return Response('Unexpected error')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    try:
        user = request.user

        try:
            order = Order.objects.get(id=pk)
            if user.is_staff or order.user == user:
                serializer = OrderSerializer(order, many=False)
                return Response(serializer.data)
            else:
                Response({'detail': 'Not authorized to view this order'},
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response('Unexpected error')

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    try:
        order = Order.objects.get(id=pk)

        order.isPaid = True
        order.paidAt = datetime.now()
        order.save()

        return Response('Order was paid')
    except:
        return Response('Unexpected error')

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    try:
        order = Order.objects.get(id=pk)

        if not order.isDelivered:
            # Update the sales quantities for each book in the order
            order_items = order.orderitem_set.all()
            for order_item in order_items:
                book = order_item.book
                book.numOfSales += order_item.qty  # Increase the sales quantity for the book
                book.save()  # Save the changes

            # Update the order status to delivered and set the delivered date and time
            order.isDelivered = True
            order.deliveredAt = datetime.now()
            order.save()

            return Response('Order was delivered')

        else:
            return Response('Order already delivered')


    except Order.DoesNotExist:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

