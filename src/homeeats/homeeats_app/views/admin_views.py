from django.shortcuts import render
from ..models import Cook, Customer, Dish_Review, Order, CookChangeRequest, Address
import json
from django.template.defaulttags import register

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

@register.filter
def getvalue(d, key):
    return d.get(key)

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
    context = {
        'cook':cook,
        'orders':orders,
        'cooksplits':cooksplits,
        'oursplits':oursplits,
        'total':total,
        'total_cooksplit':total_cooksplit,
        'total_oursplit':total_oursplit
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
        print(request.POST)
        if 'delete' in request.POST:
            review.delete()
        elif 'ban' in request.POST:
            customer = Customer.objects.get(id=review.customer.id)
            print(customer)
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