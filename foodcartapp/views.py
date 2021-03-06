from django.templatetags.static import static
from django.http import JsonResponse
from django.db import transaction
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response

from foodcartapp.models import Product, OrderProduct, Order, Banner
from foodcartapp.serializers import OrderSerializer, OrderProductSerializer, BannerSerializer


@api_view(['GET'])
def banners_list_api(request):
    banners = Banner.objects.all()
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data, status=200)


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'ingredients': product.ingredients,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not serializer.validated_data['order_products']:
        content = {'message': 'order_product can not be empty'}
        return Response(content, status=400)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    request.session[f'order_{order.pk}'] = order.pk

    products_in_order = serializer.validated_data['order_products']
    order_products = [OrderProduct(order=order, **fields) for fields in products_in_order]

    for order_product in order_products:
        order_product.product_cost = order_product.product.price

    OrderProduct.objects.bulk_create(order_products)

    created_order = Order.objects.get(pk=order.pk)
    serializer = OrderSerializer(created_order)

    return Response(serializer.data, status=201)


@api_view(['GET', 'DELETE', 'PATCH'])
def handle_order_detail(request, pk):
    try:
        request.session[f'order_{pk}']
    except KeyError:
        message = 'Your order does not in database. Please check order number again'
        return Response({'message': message}, status=400)

    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'message': 'The order does not exist'}, status=404)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    if request.method == 'DELETE':
        order.delete()
        return Response({'message': 'The order was deleted successfully!'}, status=204)

    if request.method == 'PATCH':
        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
