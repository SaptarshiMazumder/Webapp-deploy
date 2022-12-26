from operator import is_
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from page3.models import Profile

# from PostIT.page3.models import Profile

from .forms import SignUpForm, EditProfileForm, PasswordChangingForm, ProfileForm

# Create your views here.


# class UserRegisterView(generic.CreateView):
#     form_class = UserCreationForm
#     template_name = 'registration/register.html'
#     success_url = reverse_lazy('login')


def register(request):
    # form = UserCreationForm()
    form = SignUpForm()
    if request.method == 'POST':
        print(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            print(data['username'])
            print(data['password1'])
            # print(form)

        else:
            data = form.cleaned_data
            return HttpResponse("<h1>Problem with password!</h1>")
        user = authenticate(
            request, username=data['username'], password=data['password1'])
        if user is not None:
            print("User is: ", user)
            login(request, user)
            return redirect("add-profile")
            # return redirect("home-page")
        # return redirect('login')
        else:
            # return redirect("add-profile")
            return redirect("register")
    context = {
        'form': form,
        'success_url': reverse_lazy('login-user')
    }
    return render(request, 'registration/register.html', context)


def login_user(request):
    context = {
        'result': ""
    }
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                if(user.profile):
                    print("My Profile: ", user.profile)
                    return redirect('home-page')
            except:
                return redirect("add-profile")
            return redirect('home-page')
            # Redirect to a success page.
            ...
        else:
            messages.success(request, ("There was an error loggin in"))
            return redirect('login-user')
            # Return an 'invalid login' error message.
    else:
        return render(request, 'registration/login_user.html', context)


def update_user(request):
    # form = UserCreationForm()
    # form = EditProfileForm()
    form = EditProfileForm(request.POST or None, instance=request.user)
    # if request.method == 'POST':
    #     print(request.POST)
    #     form = EditProfileForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #     else:
    #         data = form.cleaned_data
    #         return HttpResponse("<h1>Problem with password!</h1>")

    #     return redirect('login')
    # context = {
    #     'form': form,
    #     'success_url': reverse_lazy('home-page')
    # }

    context = {
        'form': form
    }

    if form.is_valid():
        form.save()
        return redirect('home-page')
    return render(request, 'registration/edit_profile.html', context)


def profile_page(request, pk):
    page_user = Profile.objects.get(id=pk)
    context = {
        'page_user': page_user,
    }
    return render(request, 'registration/user_profile.html', context)


def add_profile(request):
    form = ProfileForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = ProfileForm(request.POST, request.FILES)
        context = {
            'form': form,
            'user': request.user
        }
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('home-page')
        else:
            return render(request, 'registration/add_profile.html', context)
    else:
        form = ProfileForm()
    return render(request, 'registration/add_profile.html', context)


def edit_user_profile(request, pk):
    page_user = Profile.objects.get(id=pk)
    form = ProfileForm(request.POST or None,
                       request.FILES or None, instance=page_user)
    context = {
        'page_user': page_user,
        'form': form
    }

    if form.is_valid():
        form.save()
        return redirect('home-page')
    return render(request, 'registration/edit_user_profile.html', context)


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    # form_class = PasswordChangeForm
    success_url = reverse_lazy('password-success')


def password_success(request):
    return render(request, 'registration/password_success.html', {})
