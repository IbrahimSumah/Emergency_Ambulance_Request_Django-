from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import User
from dispatch.models import Ambulance, Hospital
from emergencies.models import EmergencyCall

class Command(BaseCommand):
    help = 'Create sample data for testing the Emergency Ambulance System'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create users
        User = get_user_model()
        
        # Create dispatcher
        dispatcher, created = User.objects.get_or_create(
            username='dispatcher1',
            defaults={
                'email': 'dispatcher@emergency.com',
                'first_name': 'John',
                'last_name': 'Dispatcher',
                'role': 'dispatcher',
                'phone_number': '+23276123456'
            }
        )
        if created:
            dispatcher.set_password('dispatcher123')
            dispatcher.save()
            self.stdout.write(f'Created dispatcher: {dispatcher.username}')
        
        # Create paramedics
        paramedic1, created = User.objects.get_or_create(
            username='paramedic1',
            defaults={
                'email': 'paramedic1@emergency.com',
                'first_name': 'Jane',
                'last_name': 'Medic',
                'role': 'paramedic',
                'phone_number': '+23276234567'
            }
        )
        if created:
            paramedic1.set_password('paramedic123')
            paramedic1.save()
            self.stdout.write(f'Created paramedic: {paramedic1.username}')
        
        paramedic2, created = User.objects.get_or_create(
            username='paramedic2',
            defaults={
                'email': 'paramedic2@emergency.com',
                'first_name': 'Mike',
                'last_name': 'Rescue',
                'role': 'paramedic',
                'phone_number': '+23276345678'
            }
        )
        if created:
            paramedic2.set_password('paramedic123')
            paramedic2.save()
            self.stdout.write(f'Created paramedic: {paramedic2.username}')

        # Create hospitals
        hospital1, created = Hospital.objects.get_or_create(
            name='Freetown General Hospital',
            defaults={
                'address': '34 Circular Road, Freetown, Sierra Leone',
                'latitude': 8.4840,
                'longitude': -13.2299,
                'phone_number': '+23222222222',
                'total_beds': 200,
                'available_beds': 45,
                'emergency_capacity': 'MODERATE',
                'specialties': 'Emergency Medicine, Trauma, Cardiology, Surgery'
            }
        )
        if created:
            self.stdout.write(f'Created hospital: {hospital1.name}')

        hospital2, created = Hospital.objects.get_or_create(
            name='Connaught Hospital',
            defaults={
                'address': 'Connaught Hospital, Freetown, Sierra Leone',
                'latitude': 8.4906,
                'longitude': -13.2317,
                'phone_number': '+23222333333',
                'total_beds': 150,
                'available_beds': 30,
                'emergency_capacity': 'HIGH',
                'specialties': 'Emergency Medicine, Pediatrics, Obstetrics, Internal Medicine'
            }
        )
        if created:
            self.stdout.write(f'Created hospital: {hospital2.name}')

        # Create ambulances
        ambulance1, created = Ambulance.objects.get_or_create(
            unit_number='AMB-001',
            defaults={
                'unit_type': 'ADVANCED',
                'status': 'AVAILABLE',
                'assigned_paramedic': paramedic1,
                'current_latitude': 8.4840,
                'current_longitude': -13.2299,
                'equipment_list': 'Defibrillator, Oxygen Tank, IV Equipment, Stretcher, First Aid Kit',
                'max_patients': 2
            }
        )
        if created:
            self.stdout.write(f'Created ambulance: {ambulance1.unit_number}')

        ambulance2, created = Ambulance.objects.get_or_create(
            unit_number='AMB-002',
            defaults={
                'unit_type': 'BASIC',
                'status': 'AVAILABLE',
                'assigned_paramedic': paramedic2,
                'current_latitude': 8.4906,
                'current_longitude': -13.2317,
                'equipment_list': 'Oxygen Tank, Stretcher, First Aid Kit, Splints',
                'max_patients': 1
            }
        )
        if created:
            self.stdout.write(f'Created ambulance: {ambulance2.unit_number}')

        ambulance3, created = Ambulance.objects.get_or_create(
            unit_number='AMB-003',
            defaults={
                'unit_type': 'CRITICAL',
                'status': 'AVAILABLE',
                'current_latitude': 8.4750,
                'current_longitude': -13.2400,
                'equipment_list': 'Advanced Life Support, Ventilator, Cardiac Monitor, Defibrillator, IV Equipment',
                'max_patients': 1
            }
        )
        if created:
            self.stdout.write(f'Created ambulance: {ambulance3.unit_number}')

        # Create sample emergency calls
        sample_call1, created = EmergencyCall.objects.get_or_create(
            caller_name='Mary Johnson',
            defaults={
                'caller_phone': '+23276111111',
                'emergency_type': 'CARDIAC',
                'description': 'Elderly man experiencing chest pain and difficulty breathing',
                'location_address': '15 Siaka Stevens Street, Freetown',
                'latitude': 8.4850,
                'longitude': -13.2310,
                'status': 'RECEIVED',
                'priority': 'HIGH'
            }
        )
        if created:
            self.stdout.write(f'Created emergency call: {sample_call1.call_id}')

        sample_call2, created = EmergencyCall.objects.get_or_create(
            caller_name='Ahmed Kamara',
            defaults={
                'caller_phone': '+23276222222',
                'emergency_type': 'TRAUMA',
                'description': 'Motorcycle accident with suspected leg fracture',
                'location_address': 'Kissy Road Junction, Freetown',
                'latitude': 8.4700,
                'longitude': -13.2200,
                'status': 'RECEIVED',
                'priority': 'MEDIUM'
            }
        )
        if created:
            self.stdout.write(f'Created emergency call: {sample_call2.call_id}')

        self.stdout.write(
            self.style.SUCCESS(
                '\nSample data created successfully!\n'
                'Login credentials:\n'
                '- Dispatcher: dispatcher1 / dispatcher123\n'
                '- Paramedic 1: paramedic1 / paramedic123\n'
                '- Paramedic 2: paramedic2 / paramedic123\n'
            )
        )
