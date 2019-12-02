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
    splits = {}
    for order in cook.order_set.all():
        splits[order.id] = float("{0:.2f}".format(float(order.total) * 0.2))
    total = 0
    for order in cook.order_set.filter(status="d"):
        total += order.total
    total_split = float("{0:.2f}".format(float(total) * 0.2))
    return render(request, 'admin_templates/cook.html', {'cook':cook,'splits':splits,'total':total,'total_split':total_split})

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
        elif 'allow' in request.POST:
            review.report_flag = False
            review.save()
    return render(request, 'admin_templates/reportedreviews.html', {'reviews':reviews})