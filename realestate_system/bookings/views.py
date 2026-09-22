import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from .models import Booking
from .forms import BookingForm
from accounts.models import User


@login_required
def booking_list(request):
    today = timezone.now().date()
    base_qs = Booking.objects.select_related('client', 'assigned_to').all()

    # Scope (all vs mine)
    scope = request.GET.get('scope', 'all' if request.user.is_superuser or request.user.role != 'AGENT' else 'mine')
    if scope == 'mine':
        qs = base_qs.filter(assigned_to=request.user)
    else:
        qs = base_qs

    # Timeframe filter (all, today, upcoming, past)
    timeframe = request.GET.get('timeframe', 'all')
    if timeframe == 'today':
        qs = qs.filter(booking_datetime__date=today)
    elif timeframe == 'upcoming':
        qs = qs.filter(booking_datetime__date__gte=today)
    elif timeframe == 'past':
        qs = qs.filter(booking_datetime__date__lt=today)

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Type filter
    type_filter = request.GET.get('type')
    if type_filter:
        qs = qs.filter(booking_type=type_filter)

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(property_address__icontains=q) |
            Q(client__full_name__icontains=q) |
            Q(client__phone__icontains=q) |
            Q(notes__icontains=q)
        )

    # KPI counts from the overall database
    total_bookings = base_qs.count()
    today_count = base_qs.filter(booking_datetime__date=today).count()
    upcoming_count = base_qs.filter(
        booking_datetime__date__gte=today,
        booking_datetime__date__lte=today + timedelta(days=7)
    ).count()
    completed_count = base_qs.filter(status='COMPLETED').count()
    confirmed_count = base_qs.filter(status='CONFIRMED').count()
    confirmed_rate = int((confirmed_count / total_bookings * 100)) if total_bookings > 0 else 0

    # Chart 1: Bookings by Type
    type_map = dict(base_qs.values('booking_type').annotate(c=Count('id')).values_list('booking_type', 'c'))
    type_keys = ['VIEWING', 'MEETING', 'SITE_VISIT', 'CALL']
    type_labels = ['Viewing', 'Meeting', 'Site Visit', 'Phone Call']
    type_counts = [type_map.get(k, 0) for k in type_keys]

    # Chart 2: Bookings by Status
    status_map = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
    status_keys = ['CONFIRMED', 'REQUESTED', 'COMPLETED', 'NOSHOW', 'CANCELLED']
    status_labels = ['Confirmed', 'Requested', 'Completed', 'No-Show', 'Cancelled']
    status_counts = [status_map.get(k, 0) for k in status_keys]

    # Chart 3: 7-Day Schedule Density (today through today + 6)
    date_labels = []
    daily_booking_counts = []
    for i in range(7):
        d = today + timedelta(days=i)
        date_labels.append(d.strftime('%a, %b %d'))
        count = base_qs.filter(booking_datetime__date=d).count()
        daily_booking_counts.append(count)

    context = {
        'bookings': qs,
        'total_bookings': total_bookings,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'confirmed_rate': confirmed_rate,
        'scope': scope,
        'timeframe': timeframe,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'q': q,
        'statuses': Booking.STATUS_CHOICES,
        'types': Booking.TYPE_CHOICES,
        'title': 'Bookings & Appointments',
        # Serialized chart data
        'type_labels_json': json.dumps(type_labels),
        'type_counts_json': json.dumps(type_counts),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'date_labels_json': json.dumps(date_labels),
        'daily_booking_counts_json': json.dumps(daily_booking_counts),
    }
    return render(request, 'bookings/list.html', context)


@login_required
def todays_bookings(request):
    return redirect('/bookings/?timeframe=today')


@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f"Booking for {booking.client.full_name} scheduled successfully.")
            return redirect('bookings:list')
    else:
        form = BookingForm()
    return render(request, 'bookings/form.html', {'form': form, 'title': 'Schedule New Appointment / Viewing'})


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f"Booking for {booking.client.full_name} updated successfully.")
            return redirect('bookings:list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/form.html', {
        'form': form,
        'title': f"Edit Booking: {booking.client.full_name}",
        'booking': booking,
    })


@login_required
def booking_status_update(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    valid_statuses = [choice[0] for choice in Booking.STATUS_CHOICES]
    if status in valid_statuses:
        booking.status = status
        booking.save()
        messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
    else:
        messages.error(request, "Invalid status choice.")
    
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else 'bookings:list')


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    can_delete = (
        request.user.is_superuser
        or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER']
        or booking.assigned_to == request.user
    )
    if not can_delete:
        messages.error(request, "You do not have permission to delete this booking.")
        return redirect('bookings:list')

    if request.method == 'POST':
        client_name = booking.client.full_name
        booking.delete()
        messages.success(request, f"Booking for '{client_name}' successfully removed.")
        return redirect('bookings:list')

    return render(request, 'bookings/confirm_delete.html', {'booking': booking})