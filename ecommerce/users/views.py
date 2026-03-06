from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, AdminUserCreateForm, AdminUserUpdateForm

# staff_member_required decorator for newer Django
staff_member_required = user_passes_test(lambda u: u.is_staff)
from .models import Profile
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):

    profile_instance, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_instance)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'profile.html', context)





@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Log out the user and redirect to login page."""
    logout(request)
    return redirect('login')





@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'user_list.html', {'users': users})


@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully")
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#users')
    else:
        form = AdminUserCreateForm()

    return render(request, 'user_form.html', {
        'form': form
    })


@staff_member_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully")
            return redirect(reverse('admin_dashboard') + '#users')
    else:
        form = AdminUserUpdateForm(instance=user)

    return render(request, 'user_form.html', {
        'form': form
    })


@staff_member_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully")
        return redirect(reverse('admin_dashboard') + '#users')

    return render(request, 'user_confirm_delete.html', {'user': user})