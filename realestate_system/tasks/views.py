import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from .models import Task
from .forms import TaskForm
from .tasks import notify_task_owner


@login_required
def task_list(request):
    today = timezone.now().date()
    base_qs = Task.objects.select_related('owner', 'related_client', 'related_booking', 'created_by').all()

    # Scope (all vs mine)
    # Default: non-superusers with role AGENT see 'mine', managers/CEO see 'all'
    default_scope = 'all' if request.user.is_superuser or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER'] else 'mine'
    scope = request.GET.get('scope', default_scope)
    if scope == 'mine':
        qs = base_qs.filter(owner=request.user)
    else:
        qs = base_qs

    # Timeframe filter
    timeframe = request.GET.get('timeframe', 'all')
    if timeframe == 'today':
        qs = qs.filter(due_date=today).exclude(status='DONE')
    elif timeframe == 'upcoming':
        qs = qs.filter(due_date__gt=today).exclude(status='DONE')
    elif timeframe == 'overdue':
        qs = qs.filter(due_date__lt=today).exclude(status='DONE')
    elif timeframe == 'completed':
        qs = qs.filter(status='DONE')
    elif timeframe == 'open':
        qs = qs.exclude(status='DONE')

    # Priority filter
    priority_filter = request.GET.get('priority')
    if priority_filter:
        qs = qs.filter(priority=priority_filter)

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Search keyword
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(related_client__full_name__icontains=q) |
            Q(owner__username__icontains=q) |
            Q(owner__first_name__icontains=q) |
            Q(owner__last_name__icontains=q)
        )

    # KPIs computed on current scope
    scope_base = base_qs.filter(owner=request.user) if scope == 'mine' else base_qs
    total_tasks = scope_base.count()
    open_tasks = scope_base.exclude(status='DONE').count()
    due_today_count = scope_base.filter(due_date=today).exclude(status='DONE').count()
    overdue_count = scope_base.filter(due_date__lt=today).exclude(status='DONE').count()
    completed_count = scope_base.filter(status='DONE').count()
    completion_rate = int((completed_count / total_tasks * 100)) if total_tasks > 0 else 0

    # Chart 1: Status Distribution
    status_map = dict(scope_base.values('status').annotate(c=Count('id')).values_list('status', 'c'))
    status_keys = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE']
    status_labels = ['To Do', 'In Progress', 'Blocked', 'Done']
    status_counts = [status_map.get(k, 0) for k in status_keys]

    # Chart 2: Priority Distribution of open tasks
    priority_map = dict(scope_base.exclude(status='DONE').values('priority').annotate(c=Count('id')).values_list('priority', 'c'))
    priority_keys = ['URGENT', 'HIGH', 'MEDIUM', 'LOW']
    priority_labels = ['Urgent', 'High', 'Medium', 'Low']
    priority_counts = [priority_map.get(k, 0) for k in priority_keys]

    context = {
        'tasks': qs,
        'total_tasks': total_tasks,
        'open_tasks': open_tasks,
        'due_today_count': due_today_count,
        'overdue_count': overdue_count,
        'completed_count': completed_count,
        'completion_rate': completion_rate,
        'scope': scope,
        'timeframe': timeframe,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'q': q,
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
        'title': 'Tasks & Operations',
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'priority_labels_json': json.dumps(priority_labels),
        'priority_counts_json': json.dumps(priority_counts),
    }
    return render(request, 'tasks/list.html', context)


@login_required
def my_tasks(request):
    """Alias for task list scoped to current user."""
    return redirect('/tasks/?scope=mine')


@login_required
def today_tasks(request):
    """Filter for tasks due today."""
    return redirect('/tasks/?timeframe=today')


@login_required
def overdue_tasks(request):
    """Filter for overdue tasks."""
    return redirect('/tasks/?timeframe=overdue')


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            notify_task_owner.delay(task.id)
            messages.success(request, f"Task '{task.title}' created and assigned to {task.owner}.")
            return redirect('tasks:list')
    else:
        form = TaskForm(initial={'owner': request.user, 'due_date': timezone.now().date()})
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    can_edit = (
        request.user.is_superuser
        or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER']
        or task.owner == request.user
        or task.created_by == request.user
    )
    if not can_edit:
        messages.error(request, "You do not have permission to edit this task.")
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f"Task '{task.title}' updated successfully.")
            return redirect('tasks:list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/form.html', {'form': form, 'title': f"Edit Task: {task.title}", 'task': task})


@login_required
def task_toggle(request, pk):
    if request.user.is_superuser or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER']:
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, owner=request.user)

    if task.status == 'DONE':
        task.status = 'TODO'
        task.completed_at = None
        messages.info(request, f"Task '{task.title}' marked as To Do.")
    else:
        task.status = 'DONE'
        task.completed_at = timezone.now()
        messages.success(request, f"Task '{task.title}' marked as completed!")
    task.save()
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('tasks:list')


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    can_delete = (
        request.user.is_superuser
        or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER']
        or task.owner == request.user
        or task.created_by == request.user
    )
    if not can_delete:
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('tasks:list')

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f"Task '{title}' has been removed.")
        return redirect('tasks:list')

    return render(request, 'tasks/confirm_delete.html', {'task': task})