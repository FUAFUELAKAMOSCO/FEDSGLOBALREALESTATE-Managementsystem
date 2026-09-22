import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from accounts.models import User
from .models import Contact
from .forms import ContactForm


@login_required
def contact_list(request):
    base_qs = Contact.objects.all()

    # If user is AGENT and not superuser/staff, allow viewing assigned, but provide 'all' filter toggle
    view_scope = request.GET.get('scope', 'all' if request.user.is_superuser or request.user.role != 'AGENT' else 'mine')
    if view_scope == 'mine':
        qs = base_qs.filter(assigned_agent=request.user)
    else:
        qs = base_qs

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(notes__icontains=q)
        )

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Source filter
    source_filter = request.GET.get('source')
    if source_filter:
        qs = qs.filter(source=source_filter)

    # Interest filter
    interest_filter = request.GET.get('interest')
    if interest_filter:
        qs = qs.filter(interest=interest_filter)

    # Agent filter
    agent_filter = request.GET.get('agent')
    if agent_filter:
        qs = qs.filter(assigned_agent_id=agent_filter)

    # Prevent N+1 queries by selecting related assigned_agent
    qs = qs.select_related('assigned_agent')

    # KPI counts based on overall pool
    total_contacts = base_qs.count()
    my_leads_count = base_qs.filter(assigned_agent=request.user).count()
    new_leads = base_qs.filter(status='NEW').count()
    negotiating_count = base_qs.filter(status='NEGOTIATING').count()
    closed_count = base_qs.filter(status='CLOSED').count()
    conversion_rate = int((closed_count / total_contacts * 100)) if total_contacts > 0 else 0

    # Chart 1: Acquisition Source Breakdown
    source_map = dict(base_qs.values('source').annotate(c=Count('id')).values_list('source', 'c'))
    source_keys = ['WEBSITE', 'WHATSAPP', 'REFERRAL', 'WALKIN', 'CALL']
    source_labels = ['Website', 'WhatsApp', 'Referral', 'Walk-in', 'Phone Call']
    source_counts = [source_map.get(k, 0) for k in source_keys]

    # Chart 2: Pipeline Status Breakdown
    status_map = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
    status_keys = ['NEW', 'CONTACTED', 'VIEWING', 'NEGOTIATING', 'CLOSED', 'LOST']
    status_labels = ['New', 'Contacted', 'Viewing', 'Negotiating', 'Closed', 'Lost']
    status_counts = [status_map.get(k, 0) for k in status_keys]

    # Chart 3: Client Interest Segmentation
    interest_map = dict(base_qs.values('interest').annotate(c=Count('id')).values_list('interest', 'c'))
    interest_keys = ['BUY', 'RENT', 'SELL', 'INVEST']
    interest_labels = ['Buy', 'Rent', 'Sell', 'Invest']
    interest_counts = [interest_map.get(k, 0) for k in interest_keys]

    agents_list = User.objects.filter(is_active=True).order_by('first_name', 'username')

    context = {
        'contacts': qs,
        'total_contacts': total_contacts,
        'my_leads_count': my_leads_count,
        'new_leads': new_leads,
        'negotiating_count': negotiating_count,
        'closed_count': closed_count,
        'conversion_rate': conversion_rate,
        'q': q,
        'status_filter': status_filter,
        'source_filter': source_filter,
        'interest_filter': interest_filter,
        'agent_filter': agent_filter,
        'view_scope': view_scope,
        'statuses': Contact.STATUS_CHOICES,
        'sources': Contact.SOURCE_CHOICES,
        'interests': Contact.INTEREST_CHOICES,
        'agents_list': agents_list,
        # Serialized chart data
        'source_labels_json': json.dumps(source_labels),
        'source_counts_json': json.dumps(source_counts),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'interest_labels_json': json.dumps(interest_labels),
        'interest_counts_json': json.dumps(interest_counts),
    }
    return render(request, 'contacts/list.html', context)


@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Contact '{contact.full_name}' successfully created.")
            return redirect('contacts:list')
    else:
        initial = {}
        if request.user.role == 'AGENT':
            initial['assigned_agent'] = request.user
        form = ContactForm(initial=initial)
    return render(request, 'contacts/form.html', {'form': form, 'title': 'Create New Contact / Lead'})


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Contact '{contact.full_name}' successfully updated.")
            return redirect('contacts:list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/form.html', {
        'form': form,
        'title': f"Edit Contact: {contact.full_name}",
        'contact': contact,
    })


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    # Check permissions: superusers, CEOs, admins, or assigned agent
    can_delete = (
        request.user.is_superuser
        or getattr(request.user, 'role', None) in ['CEO', 'ADMIN', 'FIELD_MANAGER']
        or contact.assigned_agent == request.user
    )
    if not can_delete:
        messages.error(request, "You do not have permission to delete this contact record.")
        return redirect('contacts:list')

    if request.method == 'POST':
        name = contact.full_name
        contact.delete()
        messages.success(request, f"Contact '{name}' successfully deleted.")
        return redirect('contacts:list')

    return render(request, 'contacts/confirm_delete.html', {'contact': contact})