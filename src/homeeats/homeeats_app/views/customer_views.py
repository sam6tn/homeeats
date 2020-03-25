from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm, DishReviewForm, UserEditForm, AddressEditForm, PhoneEditForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ..models import Dish, Customer, Dish_Review, Cook, Address, ShoppingCart, CartItem, Order, Item, OrderMessage
from .. import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ..decorators import customer_required
from django.forms import model_to_dict
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from decimal import Decimal
from datetime import timedelta
import urllib.request
import urllib.parse
import json
import ssl
from django.http import Http404
from django.template.defaulttags import register
import stripe
import datetime
from django.utils import timezone
import pytz
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
@customer_required
def change_current_address(request, address_id):
  customer = Customer.objects.get(user_id=request.user.id)
  cart = ShoppingCart.objects.get(customer=customer)
  current_address = Address.objects.get(
      customer=customer, current_customer_address=True)
  current_address.current_customer_address = False #changing the current address of the customer and reload the page to show items in new area
  current_address.save()
  change_address = Address.objects.get(id=address_id)
  change_address.current_customer_address = True
  change_address.save()
  if cart.empty == True:
    return HttpResponseRedirect(reverse('customer_home')) #no order currently in cart so its safe to change address (success)
  elif cart.cook in find_nearby_cooks(request):
    return HttpResponseRedirect(reverse('customer_home')) #there is an order in the cart but the chef of that order is able to deliver to the new address (success)
  else:
    change_address.current_customer_address = False
    current_address.current_customer_address = True
    current_address.save()
    change_address.save()
    #the order currently in the cart cannot be delivered to the new address so let the user know
    messages.add_message(request, messages.ERROR, "The order currently in your cart cannot deliver to this address, please complete or remove that order")
    return HttpResponseRedirect(reverse('customer_home'))

@login_required
@customer_required
def delete_address(request, address_id):
    customer = Customer.objects.get(user_id=request.user.id)
    address = Address.objects.get(id=address_id)
    if address.customer == customer:
        address.delete()
    return HttpResponseRedirect(reverse('customer_home'))


@login_required
@customer_required
def dish(request, dish_id):
    dish = Dish.objects.get(id=dish_id)  # get Dish object from dish_id
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    reviews = dish.dish_review_set.filter(report_flag=False).order_by(
        'date')  # get all reviews for that Dish
    form = DishReviewForm()
    return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews': reviews, 'form': form, 'cart_items': cart_items, 'customer':customer})


def verify_address(street, town, state):
    add = street  # format the cook_address as a url parameter
    add = add.replace(" ", "+")
    add = add + "+" + town + "+" + state
    req = urllib.request.Request('https://maps.googleapis.com/maps/api/geocode/json?address=' +
                                 add + '&key=AIzaSyCPqdytEpfi1zIU4dj8B3KddX8-b6OPJoM')
    resp_json = urllib.request.urlopen(
        req, context=ssl.SSLContext()).read().decode('utf-8')
    resp = json.loads(resp_json)
    if resp['status'] == 'OK':
        return True
    else:
        return False


@login_required
@customer_required
def home(request):
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    address = Address.objects.get(customer=customer,current_customer_address=True)
    other_addresses = Address.objects.filter(customer=customer,current_customer_address=False)
    if request.method == 'POST' and 'cuisine' in request.POST:
        form = forms.DishSearchForm(request.POST)
        if form.is_valid():
            dishes = find_nearby_dishes(request)
            data = form.cleaned_data
            search = data['search']
            sort = data['sort']
            cuisine = data['cuisine']
            if search == "" and sort == "" and cuisine == "":
                search = request.POST["search"]

            dishes = dishes.filter(title__icontains=search)

            if (not customer.shoppingcart.empty):
                dishes = dishes.filter(cook=customer.shoppingcart.cook)

            if (cuisine != 'none' and cuisine != ''):
                dishes = dishes.filter(cuisine=cuisine)

            if (sort == 'rating'):
                dishes = dishes.order_by('-rating')
            elif (sort == 'price'):
                dishes = dishes.order_by('price')
            elif (sort == 'reverse_price'):
                dishes = dishes.order_by('-price')

            return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form, 'customer': customer, 'cart_items': cart_items, 'address':address, 'other_addresses':other_addresses})
        # else:
        #     dishes = find_nearby_dishes(request)
        #     return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form, 'customer': customer, 'cart_items': cart_items, 'address':address})
    elif request.method == 'POST' and 'town' in request.POST:
        form = forms.AddressCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if verify_address(data['street'], data['town'], data['state']):
                address = Address.objects.create(
                    street_name=data['street'],
                    city=data['town'],
                    state=data['state'],
                    zipcode=data['zipcode'],
                    customer=customer
                )
                address.save()
                return HttpResponseRedirect(reverse('change_current_address', args=[address.id]))
            else:
                messages.add_message(
                    request, messages.ERROR, 'Address not valid, please try again')
                return HttpResponseRedirect(reverse('customer_home'))
        else:
            messages.add_message(
                    request, messages.ERROR, 'One or more of the fields is missing or incomplete, please try again!')
            return HttpResponseRedirect(reverse('customer_home'))
    else:
        form = forms.DishSearchForm()
        dishes = find_nearby_dishes(request)
        if (not customer.shoppingcart.empty):
            dishes = dishes.filter(cook=customer.shoppingcart.cook)
        dishes = dishes.order_by('-rating')

        return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form, 'customer': customer, 'cart_items': cart_items, 'address':address, 'other_addresses':other_addresses})


@login_required
@customer_required
def addtocart(request):
    dish = Dish.objects.get(id=request.POST["dish_id"])
    return_quantity = -1
    if request.method == "POST":
        if(dish.cook_disabled or dish.cook.online == False):
            messages.add_message(request, messages.ERROR, 'Unauthorized to perform this action')
            return HttpResponseRedirect(reverse('customer_home'))
        customer = Customer.objects.get(user_id=request.user.id)
        shopping_cart = customer.shoppingcart
        shopping_cart.total_before_tip += dish.price
        shopping_cart.item_subtotal += dish.price
        shopping_cart.total_before_tip -= shopping_cart.tax
        shopping_cart.tax = Decimal(
            round((.06 * float(shopping_cart.item_subtotal)), 2))
        shopping_cart.total_before_tip += shopping_cart.tax
        existing_already = False
        for existing_item in shopping_cart.cartitem_set.all():
            if (existing_item.dish == dish):  # dish already in cart so add to existing cart item
                existing_item.quantity += 1
                existing_item.subtotal += dish.price
                existing_item.save()
                existing_already = True
                return_quantity = existing_item.quantity
                break
        if (existing_already == False):  # dish not yet in cart so create new cart item
            cart_item = CartItem.objects.create(
                dish=dish,
                quantity=1,
                subtotal=dish.price,
                shopping_cart=shopping_cart
            )
            return_quantity = 1
            cart_item.save()
            shopping_cart.cook = dish.cook
        if shopping_cart.empty == True:
            shopping_cart.empty = False
            shopping_cart.total_before_tip += dish.cook.delivery_fee
        shopping_cart.save()
        
    data = {
        'quantity': return_quantity,
        'dish_id': request.POST["dish_id"]
    }
    if "dishbtn" in request.POST:
        return HttpResponseRedirect(reverse('customer_home'))
    else:
        return JsonResponse(data)

@login_required
@customer_required
def removefromcart(request):
    dish = Dish.objects.get(id=request.POST["dish_id"])
    return_quantity = -1
    if request.method == "POST":
        if(dish.cook_disabled or dish.cook.online == False):
            messages.add_message(request, messages.ERROR, 'Unauthorized to perform this action')
            return HttpResponseRedirect(reverse('customer_home'))
        customer = Customer.objects.get(user_id=request.user.id)
        shopping_cart = customer.shoppingcart
        shopping_cart.total_before_tip -= dish.price
        shopping_cart.item_subtotal -= dish.price
        shopping_cart.total_before_tip -= shopping_cart.tax
        shopping_cart.tax = Decimal(
            round((.06 * float(shopping_cart.item_subtotal)), 2))
        shopping_cart.total_before_tip += shopping_cart.tax
        existing_already = False
        for existing_item in shopping_cart.cartitem_set.all():
            if (existing_item.dish == dish):  # dish already in cart so add to existing cart item
                existing_item.quantity -= 1
                existing_item.subtotal -= dish.price
                existing_item.save()
                existing_already = True
                return_quantity = existing_item.quantity
                if (existing_item.quantity < 1):
                    existing_item.delete()
                break

        if shopping_cart.total_before_tip == shopping_cart.cook.delivery_fee:
            shopping_cart.cook_id = None
            shopping_cart.empty = True
            shopping_cart.total_before_tip = 0
            shopping_cart.tax = 0

        if shopping_cart.empty == True:
            shopping_cart.empty = False
            shopping_cart.total_before_tip += dish.cook.delivery_fee

        shopping_cart.save()
    data = {
        'quantity': return_quantity,
        'dish_id': request.POST["dish_id"]
    }

    return JsonResponse(data)


@login_required
@customer_required
def toggle_favorite(request):
    if request.method == "POST":
        dish = Dish.objects.get(id=request.POST["dish_id"])
        customer = Customer.objects.get(user_id=request.user.id)
        if dish in customer.favorites.all():
            customer.favorites.remove(dish)
            customer.save()
            data = {
                'status': dish.title + ' favorite removed'
            }
        else:
            customer.favorites.add(dish)
            customer.save()
            data = {
                'status': dish.title + ' favorite added'
            }

    return JsonResponse(data)

#messaging function for the customer
#gets the user from the request and creates an ordermessage object
def message(request):
    if request.method == "POST":
        message = request.POST["message"]
        user = request.user
        order = Order.objects.get(id=request.POST["order_id"])

        orderMessage = OrderMessage.objects.create(
            user=user,
            message=message,
            order=order
        )

    return HttpResponseRedirect(reverse('order', args=[order.id]))


@login_required
@customer_required
def cart(request):
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    if request.method == "POST":
        try:
          tip = round(float(request.POST.getlist("tip")[1]), 2) if request.POST.getlist("tip")[0] == "on" else round(float(request.POST.getlist("tip")[0]), 2)
          if tip < 0:
              messages.add_message(request, messages.ERROR, "The tip amount is invalid, please enter a correct amount")
              return HttpResponseRedirect(reverse('cart'))
          shopping_cart.tip = tip
          shopping_cart.special_requests = request.POST["special_requests"]
          shopping_cart.total_after_tip = float(
            shopping_cart.total_before_tip) + shopping_cart.tip

          order_time = request.POST["orderTime"]
          shopping_cart.requested_delivery_time = timezone.localtime(timezone.now())
          if(order_time=="In 30 min"):
            shopping_cart.requested_delivery_time += datetime.timedelta(minutes=30)
          elif(order_time=="In one hour"):
            shopping_cart.requested_delivery_time += datetime.timedelta(minutes=60)
          elif(order_time=="In two hours"):
            shopping_cart.requested_delivery_time += datetime.timedelta(minutes=120)
          elif(order_time=="In three hours"):
            shopping_cart.requested_delivery_time += datetime.timedelta(minutes=180)

          shopping_cart.save()
          return HttpResponseRedirect(reverse('payment'))
        except Exception as e:
          messages.add_message(request, messages.ERROR, "The tip amount is invalid, please enter a correct amount")
          return HttpResponseRedirect(reverse('cart'))

    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart).order_by('dish__title')
    cart = customer.shoppingcart
    cart.tip_options = calculate_tip_amounts(cart.total_before_tip)
    address = Address.objects.get(current_customer_address=True, customer=customer)
    return render(request, 'customer_templates/cart.html', {'cart': cart, 'cart_items': cart_items, 'address': address})

@login_required
@customer_required
def payment(request):
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    cart = customer.shoppingcart
    return render(request, 'customer_templates/payment.html', {'cart': cart, 'cart_items': cart_items, 'key': settings.STRIPE_PUBLISHABLE_KEY})


# @login_required
# @customer_required
# def removeItem(request):
#     item = CartItem.objects.get(id=request.POST["item_id"])
#     customer = Customer.objects.get(user_id=request.user.id)
#     cart = customer.shoppingcart
#     cart.total_before_tip = cart.total_before_tip - item.subtotal
#     cart.item_subtotal = cart.item_subtotal - item.subtotal
#     cart.total_before_tip -= cart.tax
#     cart.tax = Decimal(round((.06 * float(cart.item_subtotal)), 2))
#     cart.total_before_tip += cart.tax
#     if cart.total_before_tip == cart.cook.delivery_fee:
#         cart.cook_id = None
#         cart.empty = True
#         cart.total_before_tip = 0
#         cart.tax = 0
#     item.delete()
#     cart.save()
#     return HttpResponse(202, 'ok')


@register.filter
def getvalue(d, key):
    return d.get(key)

@login_required
@customer_required
def orders(request):
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    orders = customer.order_set.all()
    current_orders = customer.order_set.filter(
        Q(status='p') | Q(status='c') | Q(status='o'))
    past_orders = customer.order_set.filter(
        Q(status='d') | Q(status='r') | Q(status='x')).order_by('-date')
    deadlines = {}
    for order in current_orders:
        if order.status == 'p':
            deadlines[order.id] = order.pending_deadline
    context = {
        'current_orders': current_orders,
        'past_orders': past_orders,
        'deadlines': deadlines,
        'cart_items': cart_items,
    }
    return render(request, 'customer_templates/orders.html', context)


@login_required
@customer_required
def cancel_order(request):
    order = Order.objects.get(id=request.POST["order_id"])
    customer = Customer.objects.get(user_id=request.user.id)
    if order.customer == customer and order.status == 'p':  # make sure order belongs to customer and order was pending
        order.status = 'x'
        order.save()
    return HttpResponseRedirect(reverse('orders'))


@login_required
@customer_required
def order(request, order_id):
    order = Order.objects.get(id=order_id)
    messages = OrderMessage.objects.filter(order_id=order_id)
    if request.method == "POST":
        form = DishReviewForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            dish_id = request.POST["dish_id"]
            dish = Dish.objects.get(id=dish_id)
            item = order.item_set.get(dish=dish)
            rating_name = "rating"+dish_id
            #rating = data["dish_rating"]
            rating = request.POST[rating_name]
            text = data["description"]
            report = False
            customer = Customer.objects.get(user_id=request.user.id)

            # save the new review
            dr = Dish_Review(dish_rating=rating, description=text,
                             report_flag=report, customer=customer, dish=dish)
            dr.save()

            # add review to item
            item.review = dr
            item.save()

            # calculate new dish rating
            all_dish_reviews = Dish_Review.objects.filter(dish=dish)
            total_rating = 0
            for review in all_dish_reviews:
                total_rating += review.dish_rating
            new_rating = int(round(total_rating/len(all_dish_reviews)))
            dish.rating = new_rating
            dish.save()

        return HttpResponseRedirect(reverse('order', kwargs={'order_id': order_id}))
    else:
        form = DishReviewForm()
        reviewed_items = order.item_set.filter(review__isnull=False)
        customer = Customer.objects.get(user_id=request.user.id)
        shopping_cart = ShoppingCart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
        return render(request, 'customer_templates/order.html', {'order': order, 'form': form, 'reviewed_items': reviewed_items, 'customer': customer, 'cart_items': cart_items, 'messages': messages})


@login_required
@customer_required
def checkout(request):
    if request.method == "POST":
        if request.POST['payment_option'] == "card":
            stripe.api_key = "sk_test_X4wFRNpe69n5mSKzoDBZ4JYp00EWm97YCx"
            customer = Customer.objects.get(user_id=request.user.id)
            shopping_cart = ShoppingCart.objects.get(customer=customer)
            try:
                token = stripe.Token.create(
                    card={
                        "number": request.POST['cardNumber'],
                        "exp_month": request.POST['expDate'].split('/')[0],
                        "exp_year": request.POST['expDate'].split('/')[1],
                        "cvc": request.POST['cvc'],
                    },
                )

                charge = stripe.Charge.create(
                    amount=int(shopping_cart.total_after_tip * 100),
                    currency='usd',
                    description='Buying a meal',
                    source=token
                )
            except Exception as e:
                messages.add_message(
                    request, messages.ERROR, 'Payment not valid, please try again')
                return HttpResponseRedirect(reverse('payment'))

        customer = Customer.objects.get(user_id=request.user.id)
        shopping_cart = ShoppingCart.objects.get(customer=customer)
        order_name = request.user.first_name + " " + request.user.last_name
        order_cook = Cook.objects.get(id=shopping_cart.cook_id)
        order_cook_user = models.User.objects.get(id=order_cook.user_id)
        cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
        address = Address.objects.get(
            customer=customer, current_customer_address=True)
        homeeats_share = float(shopping_cart.item_subtotal) * .2
        cook_share = float(shopping_cart.item_subtotal) - homeeats_share + float(shopping_cart.tip) + float(order_cook.delivery_fee)
        order = Order.objects.create(  # create new pending order
            name=order_name,
            cook=order_cook,
            customer=customer,
            status='p',
            total=shopping_cart.total_after_tip,
            item_subtotal=shopping_cart.item_subtotal,
            cook_share = cook_share,
            homeeats_share = homeeats_share,
            tax=shopping_cart.tax,
            delivery_fee=order_cook.delivery_fee,
            tip=shopping_cart.tip,
            special_requests=shopping_cart.special_requests,
            street_name=address.street_name,
            city=address.city,
            state=address.state,
            zipcode=address.zipcode,
            payment_option="b",
            requested_delivery_time=shopping_cart.requested_delivery_time
        )

        if request.POST['payment_option'] == 'cash':
            order.payment_option = "a"

        order.save()
        max_cook_time = 0
        for item in cart_items:  # for each CartItem in shopping cart
            dish = Dish.objects.get(id=item.dish_id)
            if dish.cook_time > max_cook_time:
                max_cook_time = dish.cook_time
            order_item = Item.objects.create(  # create an Item for order with stuff from shopping cart
                dish=dish,
                quantity=item.quantity,
                subtotal=item.subtotal,
                order=order
            )
            order_item.save()
            item.delete()  # delete item from CartItem
        cook_address = Address.objects.get(cook=shopping_cart.cook)
        customer_address = Address.objects.get(
            customer=customer, current_customer_address=True)
        time = 5 + max_cook_time + \
            round(int(get_delivery_time(cook_address, customer_address)) / 60)
        order.estimated_arrival_time = order.date + timedelta(minutes=time)

        #sets deadline for cook to accept order before it expires
        order.pending_deadline = order.requested_delivery_time - timedelta(minutes=time)
        if (order.pending_deadline < timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5)):
            order.pending_deadline = timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5)
        
        order.save()
        shopping_cart.empty = True  # set shopping cart back to empty
        shopping_cart.total_before_tip = 0  # clear total for shopping cart
        shopping_cart.total_after_tip = 0
        shopping_cart.special_requests = ""
        shopping_cart.tip = 0
        shopping_cart.delivery_fee = 0
        shopping_cart.item_subtotal = 0
        shopping_cart.tax = 0
        shopping_cart.cook = None
        shopping_cart.save()

        messages.add_message(
          request, messages.SUCCESS, 'Your order has been submitted, go to the orders section to view order status!')
        send_mail(
            'New Order',
            'A new order has been placed you have 5 minutes to accept.',
            'capstonecustomer2020@gmail.com',
            [order_cook_user.email],
            fail_silently=False,
        )
        return HttpResponseRedirect(reverse('customer_home'))
    else:
        return HttpResponseRedirect(reverse('customer_home'))

# get the time to travel from cook_address to customer_address


def get_delivery_time(cook_address, customer_address):
    origin = cook_address.street_name  # format the cook_address as a url parameter
    origin = origin.replace(" ", "+")
    origin = origin + "+" + cook_address.city + "+" + cook_address.state
    # format the cook_address as a url parameter
    destination = customer_address.street_name
    destination = destination.replace(" ", "+")
    destination = destination + "+" + \
        customer_address.city + "+" + customer_address.state

    req = urllib.request.Request('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' +
                                 origin + '&destinations=' + destination + '&key=AIzaSyCPqdytEpfi1zIU4dj8B3KddX8-b6OPJoM')
    resp_json = urllib.request.urlopen(
        req, context=ssl.SSLContext()).read().decode('utf-8')
    resp = json.loads(resp_json)

    return resp['rows'][0]['elements'][0]['duration']['value']

# get the distance between origin and destination using google maps api


def get_distance(origin, destination):
    req = urllib.request.Request('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' +
                                 origin + '&destinations=' + destination + '&key=AIzaSyCPqdytEpfi1zIU4dj8B3KddX8-b6OPJoM')
    resp_json = urllib.request.urlopen(
        req, context=ssl.SSLContext()).read().decode('utf-8')
    resp = json.loads(resp_json)
    return resp['rows'][0]['elements'][0]['distance']['text'].strip(' mi')

# find nearby cooks by checking the distance between customer and all cooks, filtering on
# delivery distance set by cook


def find_nearby_cooks(request):
    customer = get_object_or_404(Customer, user_id=request.user.id)
    cooks = Cook.objects.all()
    cook_addresses = Address.objects.filter(is_cook_address=True)
    customer_address = Address.objects.get(
        customer=customer, current_customer_address=True)
    formatted_cook_addresses = []
    formatted_customer_address = customer_address.street_name.replace(
        " ", "+") + "+" + customer_address.city + "+" + customer_address.state  # format the customer address as a url parameter
    distance_cooks = []
    nearby_cooks = []
    for address in cook_addresses:
        add_str = address.street_name  # format the cook_address as a url parameter
        add_str = add_str.replace(" ", "+")
        add_str = add_str + "+" + address.city + "+" + address.state
        tup = (add_str, address.cook_id)
        formatted_cook_addresses.append(tup)
    for add in formatted_cook_addresses:
        distance_cook = (get_distance(
            add[0], formatted_customer_address), add[1])
        distance_cooks.append(distance_cook)
    for distance in distance_cooks:
        cook = Cook.objects.get(id=distance[1])
        dist = distance[0].replace(",", "")
        try:
          if float(dist) < cook.delivery_distance_miles:
              nearby_cooks.append(cook)
        except:
          nearby_cooks.append(cook)
    return nearby_cooks  # returning a queryset of cooks

# use find_nearby_cooks to find all nearby dishes


def find_nearby_dishes(request):
    cooks = find_nearby_cooks(request)
    dishes = Dish.objects.filter(cook__in=cooks)
    return dishes  # returning a queryset of dishes

def calculate_tip_amounts(total):
    PERCENTS = [.15, .20, .30]
    LABELS = ["15 %", "20 %", "30 %"]
    tip_amounts = []
    for index in range(len(PERCENTS)):
        tip_option = {
          "amount": round(float(total)*PERCENTS[index], 2),
          "label": LABELS[index]
        }
        tip_amounts.append(tip_option)

    return tip_amounts
'''
Allows the customer to edit their username, password, and phone number.
The form will show the customer their username, but they will not be allowed to edit it.
'''


def customer_edit_profile(request):
    current_user = models.User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = UserEditForm(request.POST,
                            request.FILES,
                            instance=request.user)
        if request.POST['first_name'] == "":
            request.POST['first_name'] = request.user.first_name
        
        phone_form = PhoneEditForm(request.POST,
                                   request.FILES,
                                   instance=request.user.customer)
        
        if form.is_valid() and phone_form.is_valid():
            data = form.cleaned_data
            phone_data = phone_form.cleaned_data
            form.save()
            phone_form.save()
            messages.add_message(request, messages.SUCCESS, "Information saved successfully!")
            return HttpResponseRedirect(reverse('myaccount'))
        else:
            if not phone_form.is_valid():
                messages.add_message(request, messages.ERROR, "Enter a valid phone number. Must be 10 digits long, e.g. 0123456789")
            #messages.add_message(request, messages.ERROR, "One or more of the fields is missing or invalid, please try again!")
            customer = Customer.objects.get(user_id=request.user.id)
            shopping_cart = ShoppingCart.objects.get(customer=customer)
            cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
            current_user.email = request.user.username
            form = UserEditForm(instance=current_user)
            phone_form = PhoneEditForm(instance=customer)
            context = {
                'cart_items': cart_items,
                'phone_form': phone_form,
                'form': form,
            }
            return render(request, 'customer_templates/customer_edit_profile.html', context)
    else:
        customer = Customer.objects.get(user_id=request.user.id)
        shopping_cart = ShoppingCart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
        current_user.email = request.user.username
        form = UserEditForm(instance=request.user)
        phone_form = PhoneEditForm(instance=request.user.customer)
        #phone_form = PhoneEditForm()
        context = {
            'cart_items': cart_items,
            'phone_form': phone_form,
            'form': form,
        }
        return render(request, 'customer_templates/customer_edit_profile.html', context)
    


@login_required
@customer_required
def favorites(request):
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    favorite_dishes = customer.favorites.all()
    context = {
        'cart_items': cart_items,
        'customer': customer,
        'dishes': favorite_dishes
    }

    return render(request, 'customer_templates/favorites.html', context)


@login_required
@customer_required
def myaccount(request):
    if request.method == 'POST':
        first_name = request.GET.get('first_name')
        last_name = request.GET.get('last_name')
        username = request.GET.get('username')
        return HttpResponseRedirect(reverse('customer_edit_profile'))
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = ShoppingCart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
    return render(request, 'customer_templates/customer_profile.html', {'cart_items': cart_items})
