from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import User
from dispatch.models import Ambulance, Hospital
from profiles.models import DispatcherProfile, ParamedicProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users and data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@emergency.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create dispatcher user
        dispatcher_user, created = User.objects.get_or_create(
            username='dispatcher1',
            defaults={
                'email': 'dispatcher@emergency.com',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'role': 'dispatcher',
                'phone_number': '+1-555-0101'
            }
        )
        if created:
            dispatcher_user.set_password('dispatch123')
            dispatcher_user.save()
            
            # Create dispatcher profile
            DispatcherProfile.objects.create(
                user=dispatcher_user,
                employee_id='DISP001',
                experience_years=5,
                certifications='Emergency Dispatch, CPR, First Aid',
                shift_schedule='Day Shift (6AM-6PM)',
                emergency_contact_name='Sarah Johnson',
                emergency_contact_phone='+1-555-0102'
            )
            self.stdout.write(self.style.SUCCESS('Created dispatcher user'))
        
        # Create paramedic users
        paramedic1, created = User.objects.get_or_create(
            username='paramedic1',
            defaults={
                'email': 'paramedic1@emergency.com',
                'first_name': 'Mike',
                'last_name': 'Rodriguez',
                'role': 'paramedic',
                'phone_number': '+1-555-0201'
            }
        )
        if created:
            paramedic1.set_password('paramedic123')
            paramedic1.save()
            
            # Create paramedic profile
            ParamedicProfile.objects.create(
                user=paramedic1,
                employee_id='PARA001',
                license_number='EMT-P-2024-001',
                experience_years=8,
                certifications='Paramedic, ACLS, PALS, Trauma',
                specialties='Critical Care, Trauma Response',
                shift_schedule='Day Shift (6AM-6PM)',
                emergency_contact_name='Maria Rodriguez',
                emergency_contact_phone='+1-555-0202'
            )
            self.stdout.write(self.style.SUCCESS('Created paramedic1 user'))
        
        paramedic2, created = User.objects.get_or_create(
            username='paramedic2',
            defaults={
                'email': 'paramedic2@emergency.com',
                'first_name': 'Jennifer',
                'last_name': 'Chen',
                'role': 'paramedic',
                'phone_number': '+1-555-0301'
            }
        )
        if created:
            paramedic2.set_password('paramedic123')
            paramedic2.save()
            
            # Create paramedic profile
            ParamedicProfile.objects.create(
                user=paramedic2,
                employee_id='PARA002',
                license_number='EMT-P-2024-002',
                experience_years=6,
                certifications='Paramedic, ACLS, PALS',
                specialties='Pediatric Care, Medical Emergencies',
                shift_schedule='Night Shift (6PM-6AM)',
                emergency_contact_name='David Chen',
                emergency_contact_phone='+1-555-0302'
            )
            self.stdout.write(self.style.SUCCESS('Created paramedic2 user'))
        
        # Create ambulances
        ambulance1, created = Ambulance.objects.get_or_create(
            unit_number='AMB-001',
            defaults={
                'unit_type': 'ADVANCED',
                'status': 'AVAILABLE',
                'current_latitude': 6.5244,
                'current_longitude': 3.3792,
                'equipment_list': 'Defibrillator, Oxygen, Stretcher, First Aid Kit, Trauma Kit',
                'max_patients': 2
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created ambulance AMB-001'))
        
        ambulance2, created = Ambulance.objects.get_or_create(
            unit_number='AMB-002',
            defaults={
                'unit_type': 'BASIC',
                'status': 'AVAILABLE',
                'current_latitude': 6.5300,
                'current_longitude': 3.3850,
                'equipment_list': 'Oxygen, Stretcher, First Aid Kit',
                'max_patients': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created ambulance AMB-002'))
        
        ambulance3, created = Ambulance.objects.get_or_create(
            unit_number='AMB-003',
            defaults={
                'unit_type': 'CRITICAL',
                'status': 'MAINTENANCE',
                'current_latitude': 6.5200,
                'current_longitude': 3.3750,
                'equipment_list': 'Advanced Life Support, Ventilator, Cardiac Monitor, IV Equipment',
                'max_patients': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created ambulance AMB-003'))
        
        # Create hospitals
        hospital1, created = Hospital.objects.get_or_create(
            name='City General Hospital',
            defaults={
                'address': '123 Medical Center Drive, Lagos',
                'latitude': 6.5400,
                'longitude': 3.4000,
                'phone_number': '+1-555-1000',
                'total_beds': 200,
                'available_beds': 45,
                'emergency_capacity': 'MODERATE',
                'specialties': 'Emergency Medicine, Cardiology, Trauma, Pediatrics'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created City General Hospital'))
        
        hospital2, created = Hospital.objects.get_or_create(
            name='Metro Medical Center',
            defaults={
                'address': '456 Health Plaza, Lagos',
                'latitude': 6.5100,
                'longitude': 3.3600,
                'phone_number': '+1-555-2000',
                'total_beds': 150,
                'available_beds': 12,
                'emergency_capacity': 'HIGH',
                'specialties': 'Emergency Medicine, Neurology, Orthopedics'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Metro Medical Center'))
        
        self.stdout.write(self.style.SUCCESS('\nSample data creation completed!'))
        self.stdout.write('\nTest Accounts:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Dispatcher: dispatcher1 / dispatch123')
        self.stdout.write('Paramedic 1: paramedic1 / paramedic123')
        self.stdout.write('Paramedic 2: paramedic2 / paramedic123')
