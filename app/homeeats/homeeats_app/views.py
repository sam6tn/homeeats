from django.shortcuts import render
from django.contrib.auth.forms import CustomerForm

class CreateProfile(generic.FormView):
    model = Profile
    login_required = True
    template_name = 'dashboard/customer_signup.html'
    
    def get(self,request):
        customer_form = CustomerForm()
        return render(request,self.template_name,{'customer_form':customer_form,})