from django.db.models import query
from django.shortcuts import redirect, render, get_object_or_404
from .forms import *
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.models import *
from carts.views import _cart_id
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from orders.models import *
from django.contrib.auth import update_session_auth_hash
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,password=password)
            user.phone_number = phone_number
            user.save()


            #user_activation
#             current_site = get_current_site(request)
#             mail_subject = 'Please activate your account'
#             message = render_to_string('accounts/account_verification_email.html', {
#                 'user' : user,
#                 'domain' : current_site,
#                 'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token' : default_token_generator.make_token(user)
#             })
#             to_email = email
#             send_email = EmailMessage(mail_subject, message, to=[to_email])
#             send_email.send()
            messages.success(request, 'Thank you for registrating with us.')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form =RegistrationForm()
    
    context= {
        'form':form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                try:
                    
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        
                        product_variation = []
                        for item in cart_item:
                            variation = item.variatons.all()
                            product_variation.append(list(variation))
                        
                        cart_item = CartItem.objects.filter(user=user)

                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        # product_variation = [1, 2, 3, 4, 6]
                        # ex_var_list = [4, 6, 3, 5]

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()

                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()

                except:
                    
                    pass
                auth.login(request,user)
                messages.success(request, 'You are now logged in')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextpage = params['next']
                        return redirect(nextpage)
                     
                except:
                    return redirect('dashboard')

            else:
                messages.error(request, 'Invalid credentials')
                return redirect('login')
        else:
            return render(request, 'accounts/login.html', {})

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')



@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders':orders,
        "orders_count": orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)


    
def forgetpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)


            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')


        else:
            messages.error(request, 'Account does not exists!')
            return redirect('forgetpassword')
    return render(request, 'accounts/forgetpassword.html', {})


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetpassword')
    
    else:
        messages.error(request, 'This link has expired!')
        return redirect('login')


def resetpassword(request):
    if request.method == 'POST':
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if password == confirm_password:
                uid = request.session.get('uid')
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful')
                return redirect('login')

            else:
                messages.error(request, 'Password do not match')
                return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')


def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    context = {
        "orders":orders,
    }
    return render(request, 'accounts/my_orders.html', context)
    

def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        context = {
            'user_form':user_form,
            'profile_form':profile_form,
            'userprofile':userprofile,
        }
    return render(request, 'accounts/edit_profile.html', context)


def change_password(request):
    if request.method == 'POST':
        
        new_password = request.POST["new_password"]
        confirmed_new_password = request.POST["confirm_password"]
        current_password = request.POST['old_password']
        
        if  new_password and confirmed_new_password:
            if request.user.is_authenticated:
                user = Account.objects.get(username= request.user.username)
                
                if current_password != user.password:
                    messages.warning(request, 'Old Password does not match')
                elif new_password != confirmed_new_password:
                    messages.warning(request, "your new password not match the confirm password !")
                    
                elif len(new_password) < 8 or new_password.lower() == new_password or \
                    new_password.upper() == new_password or new_password.isalnum() or \
                    not any(i.isdigit() for i in new_password):
                    messages.warning(request, "your password is too weak!")

                    

                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)

                    messages.success(request, "your password has been changed successfuly.!")

                    return redirect('/change_password')

        else:
            messages.warning(request, " sorry , all fields are required !")
 

    return render(request, 'accounts/change_password.html',{})


@login_required(login_url = 'login')
def order_detail(request, order_id):
    
    order = Order.objects.get(id=order_id)
    order_detail = OrderProduct.objects.filter(order_id=order.id, user=request.user)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    return render(request, 'accounts/order_detail.html',{'order_detail':order_detail,'order':order,'subtotal':subtotal})
