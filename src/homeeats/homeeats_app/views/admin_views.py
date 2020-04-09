from django.shortcuts import render
from ..models import Cook, Customer, Dish_Review, Order, CookChangeRequest, Address
from .. import forms
import json
from django.template.defaulttags import register
from decimal import *
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.contrib import messages

TWOPLACES = Decimal(10) ** -2  

def revenue(request):
    if request.method == 'POST':
        dateform = forms.DatePickerForm(request.POST)
        if dateform.is_valid():
            data = dateform.cleaned_data
            start_date = data["start_date"]
            end_date = data["end_date"]
            orders = Order.objects.filter(date__range=(start_date, end_date)).order_by('-date')
        else:
            messages.add_message(request, messages.ERROR, "Invalid Date Selection. Please Enter Valid Dates.")
            orders = Order.objects.none()
    else:
        orders = Order.objects.all().order_by('-date')
        dateform = forms.DatePickerForm()

    homeeats_splits = {}
    total_sub=0
    total_tax=0
    total_delivery=0
    total_tip=0
    total=0
    for order in orders:
        total_sub += order.item_subtotal
        total_tax += order.tax
        total_delivery += order.delivery_fee
        total_tip += order.tip
        total += order.total
        homeeats_splits[order.id] = float("{0:.2f}".format(float(order.item_subtotal) * 0.2))

    total_cook_revenue = Decimal(float(total_sub)*0.8).quantize(TWOPLACES)
    total_homeeats_revenue = Decimal(float(total_sub)*0.2).quantize(TWOPLACES)

    context = {
    'orders':orders,
    'total_revenue':total_sub,
    'total_cook_revenue':total_cook_revenue,
    'total_homeeats_revenue':total_homeeats_revenue,
    'total_delivery':total_delivery,
    'total_tax':total_tax,
    'total':total,
    'total_tip':total_tip,
    'homeeats_splits':homeeats_splits,
    'dateform':dateform
    }
    return render(request,'admin_templates/revenue.html', context)

def cookApplications(request):
    if request.method == 'POST':
        cook = Cook.objects.get(id=request.POST["id"])
        if "approve" in request.POST:
            cook.approved = True
            cook.save()
        elif "decline" in request.POST:
            cook.banned = True
            cook.save()
    pending_cooks = Cook.objects.filter(approved=False).filter(banned=False)
    return render(request,'admin_templates/cook_applications.html', {'cooks':pending_cooks})

# def cooks(request):
#     cooks = Cook.objects.all()
#     return render(request,'admin_templates/cooks.html', {'cooks':cooks})

# @register.filter
# def getvalue(d, key):
#     return d.get(key)

def cook(request,cook_id):
    cook = Cook.objects.get(id=cook_id)
    cooksplits = {}
    oursplits = {}
    total=0
    orders = Order.objects.filter(cook=cook).order_by('-date')
    for order in orders:
        cooksplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.8))
        oursplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.2))
        total += order.total
    total_cooksplit = float("{0:.2f}".format(float(total) * 0.8))
    total_oursplit = float("{0:.2f}".format(float(total) * 0.2))
    if (cook.offline_time != 0):
        online_time = cook.online_time / cook.offline_time * 100
        offline_time = (cook.offline_time - cook.online_time) / cook.offline_time * 100
    else:
        online_time = 0
        offline_time = 0
    context = {
        'cook':cook,
        'orders':orders,
        'cooksplits':cooksplits,
        'oursplits':oursplits,
        'total':total,
        'total_cooksplit':total_cooksplit,
        'total_oursplit':total_oursplit,
        'online_time':online_time,
        'offline_time':offline_time
    }
    return render(request, 'admin_templates/cook.html', context)

# def customers(request):
#     customers = Customer.objects.all()
#     return render(request, 'admin_templates/customers.html', {'customers':customers})

def customer(request,customer_id):
    customer = Customer.objects.get(id=customer_id)
    cooksplits = {}
    oursplits = {}
    total=0
    orders = Order.objects.filter(customer=customer).order_by('-date')
    for order in orders:
        cooksplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.8))
        oursplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.2))
        total += order.total
    total_cooksplit = float("{0:.2f}".format(float(total) * 0.8))
    total_oursplit = float("{0:.2f}".format(float(total) * 0.2))
    context = {
        'customer':customer,
        'orders':orders,
        'cooksplits':cooksplits,
        'oursplits':oursplits,
        'total':total,
        'total_cooksplit':total_cooksplit,
        'total_oursplit':total_oursplit
    }
    return render(request, 'admin_templates/customer.html', context)

def reportedreviews(request):
    reviews = Dish_Review.objects.filter(report_flag=True)
    if request.method == "POST":
        review = Dish_Review.objects.get(id=request.POST["id"])
        if 'delete' in request.POST:
            review.delete()
        elif 'ban' in request.POST:
            customer = Customer.objects.get(id=review.customer.id)
            customer.banned = True
            customer.save()
            review.delete()
        elif 'allow' in request.POST:
            review.report_flag = False
            review.save()
    return render(request, 'admin_templates/reportedreviews.html', {'reviews':reviews})

def changerequests(request):
    if request.method == "POST":
        change = CookChangeRequest.objects.get(id=request.POST["id"])
        if "approve" in request.POST:
            #Update Cook info
            change.cook.kitchen_license = change.kitchen_license
            change.cook.phone_number = change.phone_number
            change.cook.save()

            #Update Address info
            address = Address.objects.get(cook_id=change.cook.id)
            address.street_name = change.street_name
            address.city = change.city
            address.state = change.state
            address.zipcode = change.zipcode
            address.save()
            
            change.delete()
        elif "decline" in request.POST:
            change.delete()

    requests = CookChangeRequest.objects.all()
    address_changes = {}
    for r in requests:
        address = Address.objects.get(cook=r.cook)
        if (address.street_name != r.street_name):
            address_changes[r.cook.id] = True
        else:
            address_changes[r.cook.id] = False
    context = {
        'requests':requests,
        'address_changes':address_changes
    }
    return render(request, 'admin_templates/changerequests.html', context)