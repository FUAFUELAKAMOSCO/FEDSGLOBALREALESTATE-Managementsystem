from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import User
from .forms import UserProfileUpdateForm, UserDeleteConfirmForm


@login_required
def profile_view(request):
    user = request.user
    # Related metrics
    assigned_tasks_count = getattr(user, 'owned_tasks', None).count() if hasattr(user, 'owned_tasks') else 0
    assigned_bookings_count = getattr(user, 'assigned_bookings', None).count() if hasattr(user, 'assigned_bookings') else 0
    assigned_properties_count = getattr(user, 'assigned_properties', None).count() if hasattr(user, 'assigned_properties') else 0

    context = {
        'profile_user': user,
        'assigned_tasks_count': assigned_tasks_count,
        'assigned_bookings_count': assigned_bookings_count,
        'assigned_properties_count': assigned_properties_count,
    }
    return render(request, 'accounts/profile_view.html', context)


@login_required
def profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details and avatar have been updated successfully.")
            return redirect('accounts:profile_view')
    else:
        form = UserProfileUpdateForm(instance=user)

    context = {
        'form': form,
        'profile_user': user,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def profile_delete(request):
    user = request.user

    # Prevent deleting the only superuser
    if user.is_superuser:
        superusers_count = User.objects.filter(is_superuser=True, is_active=True).count()
        if superusers_count <= 1:
            messages.error(
                request,
                "Security Safeguard: You are the only active superuser in the system. "
                "You cannot delete this root administrator account."
            )
            return redirect('accounts:profile_view')

    if request.method == 'POST':
        form = UserDeleteConfirmForm(request.POST, user=user)
        if form.is_valid():
            username = user.username
            logout(request)
            user.delete()
            messages.success(request, f"Your profile (@{username}) has been permanently deleted from the system.")
            return redirect('properties:landing')
    else:
        form = UserDeleteConfirmForm(user=user)

    context = {
        'form': form,
        'profile_user': user,
    }
    return render(request, 'accounts/profile_delete.html', context)
