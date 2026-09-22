import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from contacts.models import Contact
from bookings.models import Booking
from tasks.models import Task
from activity.models import ActivityLog


class Command(BaseCommand):
    help = "Seed the database with rich, realistic real estate data for Fred's Real Estate"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Fred's Real Estate database...")

        # Ensure main user exists and has CEO/ADMIN privileges or proper role
        main_user = User.objects.filter(username='fuafuelakamosco').first()
        if not main_user:
            main_user = User.objects.first()

        # Create additional agents if not present
        agent_names = [
            ('sarah_mbi', 'Sarah', 'Mbi', 'AGENT', 'sarah.mbi@fredsrealestate.com', '+237 671 234 567'),
            ('david_kamga', 'David', 'Kamga', 'AGENT', 'david.kamga@fredsrealestate.com', '+237 692 345 678'),
            ('fred_manager', 'Fred', 'Nguemo', 'CEO', 'fred@fredsrealestate.com', '+237 679 798 244'),
        ]
        agents = [main_user] if main_user else []
        for username, first, last, role, email, phone in agent_names:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'email': email,
                    'phone': phone,
                    'active': True,
                    'is_staff': (role == 'CEO'),
                }
            )
            if created:
                u.set_password('FredsPass2026!')
                u.save()
            agents.append(u)

        now = timezone.now()
        today = now.date()

        # 1. Contacts Seed Data
        contact_samples = [
            ("Dr. Emmanuel Tchinda", "+237 677 889 900", "emmanuel.tchinda@clinic.cm", "REFERRAL", "BUY", 185000000, "NEGOTIATING", "Looking for 5-bedroom luxury duplex in Bastos. High priority investor."),
            ("Mme. Chantal Ndongo", "+237 699 112 233", "c.ndongo@telecom.cm", "WEBSITE", "BUY", 95000000, "VIEWING", "Interested in 3-bedroom villa in Bonapriso with garden and swimming pool."),
            ("Chief Arthur Fon", "+237 675 443 322", "arthur.fon@timbercorp.com", "WHATSAPP", "INVEST", 320000000, "NEGOTIATING", "Commercial warehouse / showroom along Akwa Douala boulevard."),
            ("Beatrice Eyong", "+237 650 998 877", "beyong@oilgas.cm", "WALKIN", "RENT", 1200000, "CONTACTED", "Furnished executive apartment near Golf Club Yaoundé for 1-year lease."),
            ("Patrick Manga", "+237 691 223 344", "patrick.manga@logistics.cm", "WEBSITE", "BUY", 65000000, "NEW", "Looking for gated community family home in Yassa Douala."),
            ("Aissatou Bello", "+237 673 887 766", "aissatou.bello@cotco.cm", "CALL", "INVEST", 140000000, "CLOSED", "Successfully closed 4-unit apartment building in Kotto Douala."),
            ("Marcelle Kouam", "+237 694 556 677", "m.kouam@agroind.com", "WHATSAPP", "SELL", 210000000, "VIEWING", "Selling prime 1,200 m² titled commercial parcel in Bonanjo."),
            ("Eng. Christian Tabi", "+237 676 001 122", "tabi.christian@minfi.gov.cm", "REFERRAL", "BUY", 80000000, "CONTACTED", "Modern 4-bedroom bungalow in Odza, Yaoundé. Wants clean land title."),
            ("Sophie Mbella", "+237 695 334 455", "sophie.mbella@fashionhub.cm", "WEBSITE", "RENT", 850000, "NEW", "Looking for commercial boutique space in Akwa shopping district."),
            ("Henri Nguema", "+237 674 221 100", "henri.nguema@bicec.cm", "CALL", "BUY", 120000000, "CLOSED", "Closed deal on seafront villa in Down Beach Limbe."),
            ("Florence Atangana", "+237 697 665 544", "f.atangana@unesco.org", "REFERRAL", "RENT", 2500000, "NEGOTIATING", "Diplomatic residence in Bastos Yaoundé. Security fence required."),
            ("Alain Fopa", "+237 670 554 433", "fopa.invest@gmail.com", "WALKIN", "INVEST", 450000000, "VIEWING", "Multi-family residential complex in Makepe Douala."),
            ("Viviane Ngassa", "+237 698 776 655", "v.ngassa@hospital.cm", "WHATSAPP", "BUY", 55000000, "LOST", "Chose a private property directly from family seller."),
            ("Gaston Ebogo", "+237 672 990 011", "gaston.ebogo@lawchambers.cm", "WEBSITE", "BUY", 175000000, "VIEWING", "Executive townhouse in Bonapriso with dedicated office space."),
            ("Carine Siewe", "+237 696 443 322", "carine.siewe@fintech.cm", "CALL", "BUY", 72000000, "NEW", "Pre-construction residential apartment in Denver Douala."),
            ("Olivier Bella", "+237 678 332 211", "olivier.bella@shipping.cm", "REFERRAL", "INVEST", 260000000, "CLOSED", "Acquired logistics parcel near Port of Kribi."),
            ("Nathalie Nkem", "+237 693 889 900", "n.nkem@ngo-africa.org", "WEBSITE", "RENT", 1500000, "CONTACTED", "Office space for 12 staff in Centre Ville Yaoundé."),
            ("Jean-Paul Biya", "+237 671 009 988", "jp.biya@aerocivil.cm", "WALKIN", "BUY", 110000000, "NEGOTIATING", "Modern minimalist villa in Santa Barbara, Yaoundé."),
        ]

        created_contacts = []
        for i, (name, phone, email, src, interest, budget, status, notes) in enumerate(contact_samples):
            agent = agents[i % len(agents)]
            c, created = Contact.objects.get_or_create(
                phone=phone,
                defaults={
                    'full_name': name,
                    'email': email,
                    'source': src,
                    'interest': interest,
                    'budget': Decimal(str(budget)),
                    'status': status,
                    'assigned_agent': agent,
                    'notes': notes,
                    'last_contact': now - timedelta(days=random.randint(0, 10), hours=random.randint(1, 12)),
                }
            )
            created_contacts.append(c)

        self.stdout.write(f"Seeded {len(created_contacts)} contacts.")

        # 2. Bookings Seed Data
        booking_samples = [
            (created_contacts[0], "Villa Palais Bastos, Avenue Rosa Parks, Yaoundé", now.replace(hour=10, minute=30), "VIEWING", "CONFIRMED", agents[0], "Client arriving with architect for structural inspection."),
            (created_contacts[1], "Résidence Les Palmiers, Rue Njo-Njo, Bonapriso Douala", now.replace(hour=14, minute=0), "VIEWING", "CONFIRMED", agents[0], "Property keys picked up from security post."),
            (created_contacts[2], "Parcelle Commerciale 22, Boulevard de la Liberté, Akwa", now.replace(hour=16, minute=30), "SITE_VISIT", "CONFIRMED", agents[1 % len(agents)], "Surveyor meeting on site with land registry documents."),
            (created_contacts[3], "Fred's Real Estate VIP Lounge, Douala", now + timedelta(days=1, hours=3), "MEETING", "REQUESTED", agents[0], "Review lease terms and deposit schedule."),
            (created_contacts[4], "Gated Estate Lot 14, Yassa Douala", now + timedelta(days=1, hours=5), "VIEWING", "REQUESTED", agents[1 % len(agents)], "First showing for Mr. Patrick Manga."),
            (created_contacts[7], "Duplex Odza Borne 10, Yaoundé", now + timedelta(days=2, hours=2), "VIEWING", "CONFIRMED", agents[0], "Client requested afternoon slot after government office hours."),
            (created_contacts[10], "Ambassadorial Villa, Bastos Yaoundé", now + timedelta(days=2, hours=6), "SITE_VISIT", "CONFIRMED", agents[0], "Embassy security delegation inspection visit."),
            (created_contacts[11], "Complexe Makepe Saint-Tropez, Douala", now + timedelta(days=3, hours=4), "VIEWING", "REQUESTED", agents[1 % len(agents)], "Investment group showing for 6 rental units."),
            (created_contacts[13], "Townhouse Bonapriso Palm Grove, Douala", now + timedelta(days=4, hours=1), "VIEWING", "CONFIRMED", agents[0], "Spouse will attend showing."),
            (created_contacts[6], "Parcelle Titled Bonanjo Port Zone, Douala", now - timedelta(days=1, hours=2), "MEETING", "COMPLETED", agents[0], "Contract signed in notary office."),
            (created_contacts[5], "Immeuble Kotto 4-Etages, Douala", now - timedelta(days=2, hours=4), "SITE_VISIT", "COMPLETED", agents[1 % len(agents)], "Final handover and meter readings."),
            (created_contacts[9], "Oceanfront Cottage, Down Beach Limbe", now - timedelta(days=3, hours=3), "CALL", "COMPLETED", agents[0], "Follow-up post deed registration."),
            (created_contacts[12], "Penthouse Bonamoussadi, Douala", now - timedelta(days=4, hours=2), "VIEWING", "CANCELLED", agents[1 % len(agents)], "Client postponed due to international travel."),
            (created_contacts[14], "Résidence Denver Prime, Douala", now + timedelta(days=5, hours=2), "CALL", "REQUESTED", agents[0], "Virtual walkthrough call via Zoom."),
        ]

        created_bookings = []
        for client, address, dt, b_type, status, assigned, notes in booking_samples:
            b, _ = Booking.objects.get_or_create(
                client=client,
                property_address=address,
                booking_datetime=dt,
                defaults={
                    'booking_type': b_type,
                    'status': status,
                    'assigned_to': assigned,
                    'notes': notes,
                }
            )
            created_bookings.append(b)

        self.stdout.write(f"Seeded {len(created_bookings)} bookings.")

        # 3. Tasks Seed Data
        task_samples = [
            ("Send Bastos Villa title deed and survey map to Dr. Tchinda", "Prepare dossier including cadastre extracts, boundary certificates, and title number 4388/Mfoundi.", agents[0], created_contacts[0], created_bookings[0], "URGENT", today, "IN_PROGRESS"),
            ("Confirm viewing time with Mme. Chantal Ndongo", "Double check property access code with Bonapriso building syndic.", agents[0], created_contacts[1], created_bookings[1], "HIGH", today, "TODO"),
            ("Prepare Akwa commercial plot purchase agreement draft", "Coordinate with Notary Maitre Ndoumbe for commercial deed draft.", agents[1 % len(agents)], created_contacts[2], created_bookings[2], "HIGH", today, "TODO"),
            ("Follow up with Chief Arthur Fon on bank guarantee", "Requested proof of funds letter from EcoBank for 320M commercial acquisition.", agents[0], created_contacts[2], None, "URGENT", today - timedelta(days=1), "TODO"),
            ("Verify municipal zoning certificate for Yassa property", "Visit Douala 3 Sub-divisional urban planning office.", agents[1 % len(agents)], created_contacts[4], None, "MEDIUM", today - timedelta(days=2), "TODO"),
            ("Draft diplomatic lease agreement for UNESCO residence", "Include standard diplomatic exit clause and maintenance riders.", agents[0], created_contacts[10], created_bookings[6], "HIGH", today + timedelta(days=1), "TODO"),
            ("Upload high-resolution photography for Limbe beachfront parcel", "Post drone footage and land demarcation on marketing portal.", agents[0], created_contacts[9], None, "LOW", today + timedelta(days=2), "IN_PROGRESS"),
            ("Inspect plumbing & generator test at Santa Barbara villa", "Ensure auxiliary power backup kicks in within 15 seconds.", agents[1 % len(agents)], created_contacts[17], None, "MEDIUM", today + timedelta(days=3), "TODO"),
            ("Collect final commission check for Kotto building closing", "Receipt voucher 2026-09/11 from buyer escrow account.", agents[0], created_contacts[5], None, "HIGH", today - timedelta(days=1), "DONE"),
            ("Send quarterly market appraisal report to Alain Fopa", "Comparative market analysis for Makepe multi-family sector.", agents[0], created_contacts[11], None, "LOW", today + timedelta(days=4), "TODO"),
            ("Update WhatsApp lead status for Carine Siewe", "Review preliminary budget and recommend Denver apartment pre-sales.", agents[1 % len(agents)], created_contacts[14], None, "MEDIUM", today, "DONE"),
            ("Archive closed file for Kribi port logistics parcel", "Ensure all physical folders are cataloged in secretariat cabinet.", agents[0], created_contacts[15], None, "LOW", today - timedelta(days=3), "DONE"),
            ("Prepare property brochure for Bonapriso Palm Grove", "Format PDF with floor plan and finishing specs.", agents[0], created_contacts[13], created_bookings[8], "MEDIUM", today + timedelta(days=2), "TODO"),
        ]

        created_tasks = []
        for title, desc, owner, client, booking, priority, due, status in task_samples:
            t, _ = Task.objects.get_or_create(
                title=title,
                owner=owner,
                defaults={
                    'description': desc,
                    'related_client': client,
                    'related_booking': booking,
                    'priority': priority,
                    'due_date': due,
                    'status': status,
                    'created_by': main_user or owner,
                    'completed_at': (now - timedelta(hours=6)) if status == 'DONE' else None,
                }
            )
            created_tasks.append(t)

        self.stdout.write(f"Seeded {len(created_tasks)} tasks.")

        # 4. Activity Logs Seed Data
        activity_samples = [
            (agents[0], created_contacts[0], "MET", "Private meeting at Bastos villa with Dr. Tchinda and his architect. Discussed swimming pool renovation budget.", "Client confirmed 185M offer pending title verification."),
            (agents[0], created_contacts[1], "CALLED", "Phone call with Mme. Chantal Ndongo regarding Bonapriso viewing schedule.", "Viewing confirmed for 2:00 PM today."),
            (agents[1 % len(agents)], created_contacts[2], "WHATSAPP", "Shared surveyor cadastral map and drone overview for Akwa commercial parcel.", "Chief Fon expressed strong satisfaction, requested notary draft."),
            (agents[0], created_contacts[3], "EMAILED", "Sent draft lease terms and inventory checklist for Bastos executive apartment.", "Awaiting feedback from employer HR department."),
            (agents[0], created_contacts[5], "NOTE", "Closing completed. Deed registered at Land Registry Office Douala. Keys handed over.", "Deal closed successfully. 5% commission collected."),
            (agents[1 % len(agents)], created_contacts[6], "MET", "Signing ceremony at Maitre Ndoumbe Notary Chambers in Bonanjo.", "Deed of sale executed. Funds deposited in escrow."),
            (agents[0], created_contacts[7], "CALLED", "Discussion with Eng. Christian Tabi regarding Odza title deed provenance.", "Client satisfied with cadastre search result."),
            (agents[0], created_contacts[8], "WHATSAPP", "Sent images of retail boutique in Akwa commercial galleria.", "Client will review with retail store manager."),
            (agents[1 % len(agents)], created_contacts[10], "MET", "Walkthrough with embassy security officer at Bastos property.", "Security parameters approved. Requesting official diplomatic lease draft."),
            (agents[0], created_contacts[11], "CALLED", "Preliminary financial projection discussion on Makepe 6-unit building.", "ROI estimated at 11.4% net annually."),
            (agents[0], created_contacts[13], "WHATSAPP", "Sent video tour of Bonapriso Palm Grove residence.", "Client confirmed weekend viewing slot."),
            (agents[1 % len(agents)], created_contacts[14], "CALLED", "Welcomed new WhatsApp inquiry regarding Denver pre-sale units.", "Needs 2-bedroom with underground parking."),
            (agents[0], created_contacts[15], "NOTE", "Received official land title certificate from Kribi cadastral delegation.", "Ready for final archiving."),
            (agents[0], created_contacts[17], "EMAILED", "Forwarded utility bills history and municipal tax clearance for Santa Barbara duplex.", "All taxes confirmed up-to-date."),
            (agents[1 % len(agents)], created_contacts[4], "CALLED", "Spoke with Patrick Manga about Yassa access road paving schedule.", "Road works scheduled to complete next month."),
            (agents[0], created_contacts[9], "WHATSAPP", "Congratulatory message on Limbe beachfront villa handover.", "Client promised referral for sister living in UK."),
        ]

        created_activities = []
        for i, (person, client, action, summary, outcome) in enumerate(activity_samples):
            a_time = now - timedelta(days=i // 3, hours=(i % 3) * 4 + 1)
            act = ActivityLog.objects.create(
                person=person,
                related_client=client,
                action=action,
                summary=summary,
                outcome=outcome,
            )
            # Update created_at to provide historical spread
            ActivityLog.objects.filter(pk=act.pk).update(created_at=a_time)
            created_activities.append(act)

        self.stdout.write(f"Seeded {len(created_activities)} activity logs.")
        self.stdout.write(self.style.SUCCESS("Fred's Real Estate seed data successfully populated!"))
