from django.shortcuts import render
from ..models import Cook, Customer, Dish_Review

def cookApplications(request):
    if request.method == 'POST':
        cook = Cook.objects.get(id=request.POST["id"])
        cook.approved = True
        cook.save()
    pending_cooks = Cook.objects.filter(approved=False)
    return render(request,'admin_templates/cook_applications.html', {'cooks':pending_cooks})

# def cooks(request):
#     cooks = Cook.objects.all()
#     return render(request,'admin_templates/cooks.html', {'cooks':cooks})

def cook(request,cook_id):
    cook = Cook.objects.get(id=cook_id)
    cooksplits = {}
    oursplits = {}
    total=0
    for order in cook.order_set.all():
        cooksplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.8))
        oursplits[order.id] = float("{0:.2f}".format(float(order.total) * 0.2))
        total += order.total
    total_cooksplit = float("{0:.2f}".format(float(total) * 0.8))
    total_oursplit = float("{0:.2f}".format(float(total) * 0.2))
    context = {
        'cook':cook,
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
    cook_totals = []
    for order in customer.order_set.all():
        cook_totals.append(str(order.total*4/5))
    return render(request, 'admin_templates/customer.html', {'customer':customer,'cook_totals':cook_totals})

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