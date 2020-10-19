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
    return Response(serializer.data)


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'ingridients': product.ingridients,
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
    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    products_in_order = serializer.validated_data['products']
    products = [OrderProduct(order=order, **fields) for fields in products_in_order]

    for product in products:
        product.payment = product.get_products_cost()

    OrderProduct.objects.bulk_create(products)

    created_order = Order.objects.get(pk=order.pk)
    serializer = OrderSerializer(created_order)

    return Response(serializer.data, status=201)
