from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
  cook = get(request)
  context = {
    'cook': cook
  }
  return render(request, 'cook_templates/cook_home.html', context)

def get(request):
  cook = get_object_or_404(models.Cook, user_id=request.user.id)
  return model_to_dict(cook)
