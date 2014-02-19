""" Opentavern Views"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from tavern.forms import UserCreateForm


@login_required
def change_password(request, template='user/change_password.html'):
    form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            context = {'form': form, 'success': True}
            return render(request, template, context)

    context = {'form': form}
    return render(request, template, context)


def signup(request, template='user/signup.html'):
    form = UserCreateForm()
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, 'You are successfully registered')
            context = {'form': form}
            return redirect('index')

    context = {'form': form}
    return render(request, template, context)
