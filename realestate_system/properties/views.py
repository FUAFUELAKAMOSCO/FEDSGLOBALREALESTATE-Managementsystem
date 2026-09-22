import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import F

from .models import Property
from .forms import InquiryForm, ScheduleVisitForm, PropertyForm
from contacts.models import Contact
from bookings.models import Booking
from activity.models import ActivityLog
from accounts.models import User


def get_default_estate():
    """Ensure the Cathedral / Blue Empire prime property record exists in the DB with complete rich data."""
    prop, created = Property.objects.get_or_create(
        slug='prime-property-behind-cathedral-blue-empire-buea',
        defaults={
            'title': 'Prime Property Located Behind Cathedral around Blue Empire',
            'subtitle': 'We are proudly launching the property located behind Cathedral around Blue Empire in Buea, Cameroon.',
            'property_type': 'LAND',
            'status': 'AVAILABLE',
            'price': 2000000.00,
            'currency': 'FCFA',
            'price_prefix': 'Starting from',
            'price_suffix': 'per 400 m² titled plot',
            'area_sqm': 400.00,
            'area_display': '400 m² (Acres & Hectares Available)',
            'topography': '100% Level / Flat Topography',
            'location': 'Behind Cathedral around Blue Empire, Buea, South West Region, Cameroon',
            'city': 'Buea',
            'region': 'South West Region',
            'country': 'Cameroon',
            'description': (
                "We are proudly launching the property located behind cathedral around blue empire in Buea, Cameroon. "
                "Strategically situated in Buea's fastest booming residential and investment corridor, this property "
                "offers pristine, 100% level topography with no slope complications, immediate building readiness, "
                "Whether you are seeking a premier site for your executive family villa, modern duplexes, or high-yield "
                "land banking, Fred's Global Real Estate guarantees legally secured tenure with transparent documentation."
            ),
            'documents': [
                {'name': 'Chief Attestation', 'desc': 'Official customary council endorsement and royal blessing'},
                {'name': 'Cadastral Site Plan', 'desc': 'Approved demarcation survey with official cadastral stamps'},
                {'name': 'Transfer of Ownership', 'desc': 'Deed of assignment executed by certified notary'},
                {'name': 'Registered Title Deed', 'desc': 'Litigation-free, unencumbered land ownership tenure'},
            ],
            'landmarks': [
                {'name': 'Regina Pacis Cathedral', 'time': '2 minute walk', 'icon': 'bi-building-fill-check', 'desc': 'Premier ecclesiastical and neighborhood landmark'},
                {'name': 'Blue Empire Junction', 'time': '1 minute walk', 'icon': 'bi-signpost-2-fill', 'desc': 'Direct paved road connectivity and neighborhood hub'},
                {'name': 'Buea Town Commercial Center', 'time': '5 minute drive', 'icon': 'bi-shop-window', 'desc': 'Banking sector, markets, and regional administrative offices'},
                {'name': 'University of Buea & Mile 17', 'time': '10 minute drive', 'icon': 'bi-mortarboard-fill', 'desc': 'UB campus, student hostels, and central motor park'},
            ],
            'features': [
                '100% Flat & Level Topography - Zero excavation required',
                'Prime location behind Cathedral around Blue Empire, Buea',
                'Surveyed perimeter with concrete boundary pillars',
                'Spacious 400 m² residential plots',
                'Acres and Hectares available for commercial or institutional investors',
                'High growth appreciation corridor in South West Cameroon',
                'Clean, dispute-free documentation guaranteed by notary',
                'Ready for immediate construction of executive villas and modern duplexes',
                'Direct graded motorable road access connecting to Buea arterial roads',
            ],
            'featured_image': 'images/hero.jpg',
            'gallery_images': [
                {'src': 'images/hero.jpg', 'caption': 'Panoramic Aerial View Behind Cathedral around Blue Empire, Buea'},
                {'src': 'images/plots.jpg', 'caption': 'Demarcated 400 m² Plots with Permanent Boundary Survey Pillars'},
                {'src': 'images/plan.jpg', 'caption': 'Approved Cadastral Master Site Layout Plan'},
                {'src': 'images/villas.jpg', 'caption': 'Executive Villa Potential behind Cathedral around Blue Empire'},
            ],
            'is_featured': True,
        }
    )
    return prop


def landing_page(request, slug=None):
    if slug:
        return redirect('properties:detail', slug=slug)

    prop = Property.objects.filter(is_featured=True).first()
    if not prop:
        prop = get_default_estate()

    # Track views count
    Property.objects.filter(pk=prop.pk).update(views_count=F('views_count') + 1)
    prop.refresh_from_db(fields=['views_count'])

    # Other properties for showcase
    other_properties = Property.objects.exclude(pk=prop.pk)[:3]

    inquiry_form = InquiryForm()
    schedule_form = ScheduleVisitForm(initial={'visit_date': (timezone.now() + datetime.timedelta(days=2)).date()})

    context = {
        'property': prop,
        'other_properties': other_properties,
        'inquiry_form': inquiry_form,
        'schedule_form': schedule_form,
        'is_landing': True,
    }
    return render(request, 'properties/landing.html', context)


def property_detail(request, slug):
    prop = get_object_or_404(Property, slug=slug)

    # Track views count
    Property.objects.filter(pk=prop.pk).update(views_count=F('views_count') + 1)
    prop.refresh_from_db(fields=['views_count'])

    # Other properties for recommendations
    other_properties = Property.objects.exclude(pk=prop.pk).filter(status='AVAILABLE')[:3]
    if not other_properties.exists():
        other_properties = Property.objects.exclude(pk=prop.pk)[:3]

    inquiry_form = InquiryForm()
    schedule_form = ScheduleVisitForm(initial={'visit_date': (timezone.now() + datetime.timedelta(days=2)).date()})

    context = {
        'property': prop,
        'other_properties': other_properties,
        'inquiry_form': inquiry_form,
        'schedule_form': schedule_form,
    }
    return render(request, 'properties/property_detail.html', context)


@login_required
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save()

            staff = request.user if request.user.is_authenticated else None
            if staff:
                ActivityLog.objects.create(
                    person=staff,
                    action='NOTE',
                    summary=f"New property listed: '{prop.title}' in {prop.location}.",
                    outcome=f"Property published with slug {prop.slug} (Price: {prop.formatted_price})."
                )

            # Record immutable event on Blockchain
            try:
                from dashboard.blockchain import record_blockchain_event
                record_blockchain_event(
                    action_type='PROPERTY_CREATE',
                    record_id=str(prop.id),
                    payload={
                        'title': prop.title,
                        'price': str(prop.price),
                        'currency': prop.currency,
                        'location': prop.location,
                        'slug': prop.slug,
                    },
                    user=staff
                )
            except Exception:
                pass

            messages.success(request, f"Property '{prop.title}' has been successfully uploaded and published!")
            return redirect('properties:detail', slug=prop.slug)
        else:
            messages.error(request, "Please check the form for required fields or invalid values.")
    else:
        initial_data = {
            'city': 'Buea',
            'region': 'South West Region',
            'country': 'Cameroon',
            'currency': 'FCFA',
            'price_prefix': 'Starting from',
            'price_suffix': 'per 400 m² titled plot',
            'topography': '100% Level / Flat Topography',
            'location': 'Mile 18 Junction Buea, Cameroon',
            'assigned_agent': request.user if request.user.is_authenticated else None,
        }
        form = PropertyForm(initial=initial_data)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'title': 'Upload New Property Listing',
        'is_create': True
    })


@login_required
def property_edit(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            prop = form.save()
            messages.success(request, f"Property '{prop.title}' updated successfully!")
            return redirect('properties:detail', slug=prop.slug)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = PropertyForm(instance=prop)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'property': prop,
        'title': f'Edit Property: {prop.title}',
        'is_create': False
    })


def property_inquire(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            code = form.cleaned_data['country_code']
            raw_phone = form.cleaned_data['phone']
            full_phone = f"{code} {raw_phone}".strip() if not raw_phone.startswith('+') else raw_phone
            msg = form.cleaned_data['message']

            # Find or create contact lead in CRM
            contact = Contact.objects.filter(phone=full_phone).first()
            if not contact:
                agent = prop.assigned_agent or User.objects.filter(role__in=['AGENT', 'CEO', 'ADMIN'], is_active=True).first()
                contact = Contact.objects.create(
                    full_name=name,
                    phone=full_phone,
                    email=email,
                    source='WEBSITE',
                    interest='BUY',
                    budget=prop.price,
                    status='NEW',
                    assigned_agent=agent,
                    notes=f"Website inquiry on {prop.title}:\n\n{msg}",
                    last_contact=timezone.now(),
                )
            else:
                contact.notes = f"{contact.notes}\n\n[New Website Inquiry - {timezone.now():%Y-%m-%d %H:%M}]:\n{msg}"
                contact.last_contact = timezone.now()
                contact.save()

            # Log Activity
            staff = prop.assigned_agent or User.objects.first()
            if staff:
                ActivityLog.objects.create(
                    person=staff,
                    related_client=contact,
                    action='WHATSAPP' if 'whatsapp' in msg.lower() else 'NOTE',
                    summary=f"Website lead inquiry received from {name} regarding '{prop.title}'.",
                    outcome="Pending agent outreach & brochure dispatch.",
                )

            # Create Real-time Notification & Record to Blockchain
            try:
                from dashboard.models import Notification
                from dashboard.blockchain import record_blockchain_event
                Notification.objects.create(
                    recipient=contact.assigned_agent,
                    title=f"New Lead Inquiry: {name}",
                    message=f"Inquiry received regarding '{prop.title}'. Phone: {full_phone}",
                    notification_type='INQUIRY',
                    link=f"/contacts/{contact.id}/edit/",
                )
                record_blockchain_event(
                    action_type='INQUIRY_RECEIVED',
                    record_id=str(contact.id),
                    payload={
                        'lead_name': name,
                        'phone': full_phone,
                        'property_slug': prop.slug,
                        'interest': contact.interest,
                    }
                )
            except Exception:
                pass

            messages.success(
                request,
                f"Thank you, {name}! Your inquiry for {prop.title} has been received. "
                f"Our senior property consultant in Buea will contact you within 15 minutes."
            )
            return redirect(f"{prop.get_absolute_url()}#inquire-success")
        else:
            messages.error(request, "Please check the inquiry form fields and try again.")
    return redirect(prop.get_absolute_url())


def property_book_visit(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = ScheduleVisitForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['full_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data.get('email', '')
            v_date = form.cleaned_data['visit_date']
            v_time = form.cleaned_data['visit_time']
            v_type = form.cleaned_data['visit_type']
            notes = form.cleaned_data.get('notes', '')

            # Combine date and time
            booking_dt = timezone.make_aware(
                datetime.datetime.combine(v_date, v_time),
                timezone.get_current_timezone()
            )

            # Find or create contact
            contact = Contact.objects.filter(phone=phone).first()
            agent = prop.assigned_agent or User.objects.filter(role__in=['AGENT', 'CEO', 'ADMIN'], is_active=True).first()
            if not contact:
                contact = Contact.objects.create(
                    full_name=name,
                    phone=phone,
                    email=email,
                    source='WEBSITE',
                    interest='BUY',
                    budget=prop.price,
                    status='VIEWING',
                    assigned_agent=agent,
                    notes=f"Scheduled {v_type} for {prop.title}. Notes: {notes}",
                    last_contact=timezone.now(),
                )
            else:
                contact.status = 'VIEWING'
                contact.last_contact = timezone.now()
                contact.save()

            # Create Booking in CRM
            booking = Booking.objects.create(
                client=contact,
                property_address=f"{prop.title} - {prop.location}",
                booking_datetime=booking_dt,
                booking_type=v_type,
                status='REQUESTED',
                assigned_to=agent,
                notes=f"Public tour request. Special notes: {notes or 'None'}",
            )

            # Log Activity
            if agent:
                ActivityLog.objects.create(
                    person=agent,
                    related_client=contact,
                    action='MET' if v_type == 'SITE_VISIT' else 'CALLED',
                    summary=f"Site inspection tour scheduled by {name} for {booking_dt:%b %d, %Y at %H:%M}.",
                    outcome="Booking #{} created - Shuttle / Agent assignment pending confirmation.".format(booking.id),
                )

            # Create Notification & Record to Blockchain
            try:
                from dashboard.models import Notification
                from dashboard.blockchain import record_blockchain_event
                Notification.objects.create(
                    recipient=agent,
                    title=f"New Booking: {name}",
                    message=f"Site visit scheduled for '{prop.title}' on {booking_dt:%b %d, %Y at %H:%M}",
                    notification_type='BOOKING',
                    link=f"/bookings/{booking.id}/edit/",
                )
                record_blockchain_event(
                    action_type='BOOKING_SCHEDULED',
                    record_id=str(booking.id),
                    payload={
                        'client_name': name,
                        'booking_type': v_type,
                        'datetime': booking_dt.isoformat(),
                        'property': prop.title,
                    }
                )
            except Exception:
                pass

            messages.success(
                request,
                f"Booking Confirmed! You have requested a {v_type.replace('_', ' ').title()} on {booking_dt:%A, %B %d, %Y at %H:%M}. "
                f"Our team will reach out via WhatsApp/Phone to confirm logistics."
            )
            return redirect(f"{prop.get_absolute_url()}#visit-confirmed")
        else:
            messages.error(request, "Please check your booking date, time and contact details.")
    return redirect(prop.get_absolute_url())


def properties_catalog(request):
    properties = Property.objects.all()
    return render(request, 'properties/catalog.html', {'properties': properties})
