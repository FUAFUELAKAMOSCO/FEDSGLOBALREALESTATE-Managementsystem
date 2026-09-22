import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q, Count
from .models import ActivityLog
from .forms import ActivityLogForm


@login_required
def activity_list(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)
    base_qs = ActivityLog.objects.select_related('person', 'related_client').all()

    # Scope (all vs mine)
    default_scope = 'all' if request.user.is_superuser or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER'] else 'mine'
    scope = request.GET.get('scope', default_scope)
    if scope == 'mine':
        qs = base_qs.filter(person=request.user)
    else:
        qs = base_qs

    # Action channel filter
    action_filter = request.GET.get('action')
    if action_filter:
        qs = qs.filter(action=action_filter)

    # Timeframe filter
    timeframe = request.GET.get('timeframe', 'all')
    if timeframe == 'today':
        qs = qs.filter(created_at__date=today)
    elif timeframe == 'week':
        qs = qs.filter(created_at__date__gte=seven_days_ago)
    elif timeframe == 'month':
        thirty_days_ago = today - timedelta(days=30)
        qs = qs.filter(created_at__date__gte=thirty_days_ago)

    # Search keyword
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(summary__icontains=q) |
            Q(outcome__icontains=q) |
            Q(related_client__full_name__icontains=q) |
            Q(person__username__icontains=q) |
            Q(person__first_name__icontains=q) |
            Q(person__last_name__icontains=q)
        )

    # KPI counts on current scope
    scope_base = base_qs.filter(person=request.user) if scope == 'mine' else base_qs
    total_activities = scope_base.count()
    calls_count = scope_base.filter(action='CALLED').count()
    whatsapp_count = scope_base.filter(action='WHATSAPP').count()
    meetings_count = scope_base.filter(action='MET').count()
    today_velocity = scope_base.filter(created_at__date=today).count()

    # Chart 1: Activity Channels
    action_map = dict(scope_base.values('action').annotate(c=Count('id')).values_list('action', 'c'))
    action_keys = ['CALLED', 'WHATSAPP', 'MET', 'EMAILED', 'NOTE']
    action_labels = ['Phone Call', 'WhatsApp', 'Meeting', 'Email', 'Note']
    action_counts = [action_map.get(k, 0) for k in action_keys]

    # Chart 2: 7-Day Velocity Trend
    trend_map = dict(
        scope_base.filter(created_at__date__gte=seven_days_ago, created_at__date__lte=today)
        .values('created_at__date')
        .annotate(c=Count('id'))
        .values_list('created_at__date', 'c')
    )
    date_labels = []
    daily_velocity = []
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        date_labels.append(d.strftime('%a, %b %d'))
        daily_velocity.append(trend_map.get(d, 0))

    context = {
        'activities': qs[:150],
        'total_activities': total_activities,
        'calls_count': calls_count,
        'whatsapp_count': whatsapp_count,
        'meetings_count': meetings_count,
        'today_velocity': today_velocity,
        'scope': scope,
        'action_filter': action_filter,
        'timeframe': timeframe,
        'q': q,
        'actions': ActivityLog.ACTION_CHOICES,
        'title': 'Activity & Interaction Velocity',
        'action_labels_json': json.dumps(action_labels),
        'action_counts_json': json.dumps(action_counts),
        'date_labels_json': json.dumps(date_labels),
        'daily_velocity_json': json.dumps(daily_velocity),
    }
    return render(request, 'activity/list.html', context)


@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.person = request.user
            log.save()
            messages.success(request, f'Activity log ({log.get_action_display()}) recorded successfully.')
            return redirect('activity:list')
    else:
        client_id = request.GET.get('client')
        initial = {'related_client': client_id} if client_id else {}
        form = ActivityLogForm(initial=initial)
    return render(request, 'activity/form.html', {'form': form, 'title': 'Log Client Interaction'})