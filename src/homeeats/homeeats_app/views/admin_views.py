from django.shortcuts import render
from ..models import Cook, Customer

def cookApplications(request):
    if request.method == 'POST':
        cook = Cook.objects.get(id=request.POST["id"])
        cook.approved = True
        cook.save()
    pending_cooks = Cook.objects.filter(approved=False)
    return render(request,'admin_templates/cook_applications.html', {'cooks':pending_cooks})

def cooks(request):
    cooks = Cook.objects.all()
    return render(request,'admin_templates/cooks.html', {'cooks':cooks})

def cook(request,cook_id):
    cook = Cook.objects.get(id=cook_id)
    return render(request, 'admin_templates/cook.html', {'cook':cook})

def customers(request):
    customers = Customer.objects.all()
    return render(request, 'admin_templates/customers.html', {'customers':customers})

def customer(request,customer_id):
    customer = Customer.objects.get(id=customer_id)
    cook_totals = []
    for order in customer.order_set.all():
        cook_totals.append(str(order.total*4/5))
    return render(request, 'admin_templates/customer.html', {'customer':customer,'cook_totals':cook_totals})