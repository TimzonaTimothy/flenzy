from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
import requests
from carts.models import CartItem
from .forms import *
from .models import *
from datetime import datetime, date
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json
from django.contrib import messages
from store.models import *
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from django.dispatch import receiver
# Create your views here.


@login_required(login_url='login')
def payments(request):
    if request.is_ajax():
        amount = request.POST.get('amount', False)
        ref =  request.POST.get('ref', False)
        order_id =  request.POST.get('order_id', False)
        user = request.user
        amount = float(amount)

        # saving the payment
        order = Order.objects.get(user=request.user,is_ordered=False, order_number=ref)
        if request.user.is_authenticated:
            deposit = Payment.objects.create(amount_paid=amount,ref=ref,user=user,)
            deposit.verified = True
            deposit.save();
            
            
            order.payment = deposit
            order.status = 'Completed'
            order.is_ordered = True
            order.save()

            # moving the cartitem to order prodcut table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = order.payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                # redcuing the quantity
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()



            #deleting the cart
            CartItem.objects.filter(user=request.user).delete()

            #send mail
            # mail_subject = 'Thank you for your order!'
            # message = render_to_string('orders/order_received_email.html', {
            #     'user' : user,
            #     'order':order,
            # })
            # to_email = request.user.email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.send()

            deposited = True
            if deposited == True:
                
                
                 
                return JsonResponse({'deposited':deposited})
    
    



@login_required(login_url='login')
def place_order(request):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax 

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
              
                
            yr = int(date.today().strftime('%Y'))
            dt = int(date.today().strftime('%d'))
            mt = int(date.today().strftime('%m'))
            d = date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)+str(request.user.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')

@login_required(login_url='login')
def order_complete(request,):
    ref = request.GET.get('ref')

    
    try:
        order = Order.objects.get(user=request.user,order_number=ref, is_ordered=True)
        paid = Payment.objects.get(ref=ref,user=request.user) 
        ordered_products = OrderProduct.objects.filter(order_id=order.id, user=request.user)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity 
        
        context={
            'paid':paid,
            'order':order,
            'ordered_products':ordered_products,
            'subtotal':subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except(Payment.DoesNotExist):
        return redirect('/')
    


