#!/usr/bin/env python3
"""
Communication Emergency Plan Template
Comprehensive family communication planning for various emergency scenarios
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class CommunicationEmergencyPlan:
    def __init__(self):
        self.family_info = {}
        self.contacts = {}
        self.communication_plan = {}
        self.scenarios = {}
        
    def collect_family_information(self):
        """Collect basic family and contact information"""
        print("=== FAMILY COMMUNICATION EMERGENCY PLAN ===\n")
        
        # Basic family information
        print("1. FAMILY INFORMATION")
        self.family_info['family_name'] = input("Family name: ")
        self.family_info['home_address'] = input("Home address: ")
        self.family_info['home_phone'] = input("Home phone (if any): ")
        
        # Family members
        num_members = int(input("Number of family members: "))
        members = []
        
        for i in range(num_members):
            print(f"\nFamily Member {i+1}:")
            member = {
                'name': input("  Name: "),
                'age': int(input("  Age: ")),
                'cell_phone': input("  Cell phone: "),
                'email': input("  Email: "),
                'work_school': input("  Work/School location: "),
                'work_school_phone': input("  Work/School phone: "),
                'medical_conditions': input("  Medical conditions (if any): "),
                'medications': input("  Medications (if any): ")
            }
            members.append(member)
        
        self.family_info['members'] = members
        return self.family_info
    
    def collect_emergency_contacts(self):
        """Collect comprehensive emergency contact information"""
        print("\n2. EMERGENCY CONTACTS")
        
        contacts = {}
        
        # Out-of-state contact
        print("\nOut-of-State Emergency Contact (primary):")
        contacts['out_of_state_primary'] = {
            'name': input("  Name: "),
            'relationship': input("  Relationship: "),
            'phone': input("  Phone: "),
            'email': input("  Email: "),
            'address': input("  Address: ")
        }
        
        # Local emergency contacts
        print("\nLocal Emergency Contacts:")
        num_local = int(input("Number of local emergency contacts (recommended 3-5): "))
        local_contacts = []
        
        for i in range(num_local):
            print(f"\nLocal Contact {i+1}:")
            contact = {
                'name': input("  Name: "),
                'relationship': input("  Relationship: "),
                'phone': input("  Phone: "),
                'email': input("  Email: "),
                'address': input("  Address: "),
                'has_key': input("  Has house key? (y/n): ").lower() == 'y',
                'can_pick_up_children': input("  Authorized to pick up children? (y/n): ").lower() == 'y'
            }
            local_contacts.append(contact)
        
        contacts['local'] = local_contacts
        
        # Workplace/School contacts
        print("\nWorkplace/School Emergency Contacts:")
        workplace_contacts = []
        
        for member in self.family_info['members']:
            if member['work_school']:
                print(f"\nContacts for {member['name']} at {member['work_school']}:")
                contact = {
                    'member_name': member['name'],
                    'location': member['work_school'],
                    'main_phone': member['work_school_phone'],
                    'emergency_contact_name': input("  Emergency contact name: "),
                    'emergency_contact_phone': input("  Emergency contact phone: "),
                    'supervisor_name': input("  Supervisor/Teacher name: "),
                    'supervisor_phone': input("  Supervisor/Teacher phone: ")
                }
                workplace_contacts.append(contact)
        
        contacts['workplace_school'] = workplace_contacts
        
        # Service providers
        print("\nService Provider Contacts:")
        service_contacts = {
            'family_doctor': {
                'name': input("Family doctor name: "),
                'phone': input("Family doctor phone: "),
                'after_hours': input("After-hours number: ")
            },
            'pediatrician': {
                'name': input("Pediatrician name (if applicable): "),
                'phone': input("Pediatrician phone: ")
            },
            'veterinarian': {
                'name': input("Veterinarian name (if pets): "),
                'phone': input("Veterinarian phone: ")
            },
            'insurance_agent': {
                'name': input("Insurance agent name: "),
                'phone': input("Insurance agent phone: "),
                'company': input("Insurance company: ")
            },
            'utilities': {
                'electric_company': input("Electric company phone: "),
                'gas_company': input("Gas company phone: "),
                'water_company': input("Water company phone: "),
                'internet_provider': input("Internet provider phone: ")
            }
        }
        
        contacts['services'] = service_contacts
        
        self.contacts = contacts
        return contacts
    
    def establish_meeting_points(self):
        """Establish primary and secondary meeting points"""
        print("\n3. MEETING POINTS")
        
        meeting_points = {}
        
        # Primary meeting point (near home)
        print("\nPrimary Meeting Point (near home):")
        meeting_points['primary'] = {
            'name': input("  Location name: "),
            'address': input("  Address: "),
            'phone': input("  Phone number: "),
            'why_chosen': input("  Why this location: "),
            'backup_contact': input("  Backup contact at location: ")
        }
        
        # Secondary meeting point (outside neighborhood)
        print("\nSecondary Meeting Point (outside neighborhood):")
        meeting_points['secondary'] = {
            'name': input("  Location name: "),
            'address': input("  Address: "),
            'phone': input("  Phone number: "),
            'why_chosen': input("  Why this location: "),
            'backup_contact': input("  Backup contact at location: ")
        }
        
        # Regional evacuation point
        print("\nRegional Evacuation Point (outside city/county):")
        meeting_points['evacuation'] = {
            'name': input("  Location name: "),
            'address': input("  Address: "),
            'phone': input("  Phone number: "),
            'distance_from_home': input("  Distance from home: "),
            'estimated_travel_time': input("  Estimated travel time: ")
        }
        
        return meeting_points
    
    def create_communication_protocols(self):
        """Create communication protocols for different scenarios"""
        print("\n4. COMMUNICATION PROTOCOLS")
        
        protocols = {}
        
        # Primary communication methods
        print("\nPrimary Communication Methods (in order of preference):")
        methods = []
        for i in range(3):
            method = input(f"  Method {i+1}: ")
            if method:
                methods.append(method)
        protocols['primary_methods'] = methods
        
        # Social media protocols
        print("\nSocial Media Emergency Protocols:")
        protocols['social_media'] = {
            'facebook_page': input("  Family Facebook page/group: "),
            'twitter_hashtag': input("  Family emergency hashtag: "),
            'other_platforms': input("  Other platforms to use: "),
            'designated_poster': input("  Who posts updates: ")
        }
        
        # Check-in schedule
        print("\nCheck-in Schedule:")
        protocols['check_in'] = {
            'frequency_normal': input("  Normal check-in frequency: "),
            'frequency_emergency': input("  Emergency check-in frequency: "),
            'check_in_times': input("  Specific check-in times: "),
            'missed_check_in_protocol': input("  What to do if someone misses check-in: ")
        }
        
        # Information sharing
        print("\nInformation Sharing Protocols:")
        protocols['information_sharing'] = {
            'who_contacts_extended_family': input("  Who contacts extended family: "),
            'who_contacts_employers': input("  Who contacts employers/schools: "),
            'who_posts_social_media': input("  Who posts social media updates: "),
            'information_relay_chain': input("  Information relay chain: ")
        }
        
        return protocols
    
    def create_scenario_specific_plans(self):
        """Create communication plans for specific emergency scenarios"""
        print("\n5. SCENARIO-SPECIFIC COMMUNICATION PLANS")
        
        scenarios = {}
        
        # Scenario 1: Family separated during emergency
        print("\nScenario 1: Family Separated During Emergency")
        scenarios['family_separated'] = {
            'description': 'Family members in different locations when emergency occurs',
            'immediate_actions': [
                input("  First action: "),
                input("  Second action: "),
                input("  Third action: ")
            ],
            'communication_priority': input("  Communication priority order: "),
            'meeting_point': input("  Which meeting point to use: "),
            'time_limit': input("  Time limit before escalating: "),
            'escalation_plan': input("  Escalation plan: ")
        }
        
        # Scenario 2: Home evacuation
        print("\nScenario 2: Home Evacuation Required")
        scenarios['home_evacuation'] = {
            'description': 'Must evacuate home immediately',
            'notification_method': input("  How to notify family members: "),
            'meeting_point': input("  Evacuation meeting point: "),
            'communication_hub': input("  Communication hub person: "),
            'status_update_method': input("  How to provide status updates: "),
            'return_home_signal': input("  Signal for safe return home: ")
        }
        
        # Scenario 3: Communication systems down
        print("\nScenario 3: Communication Systems Down")
        scenarios['communications_down'] = {
            'description': 'Phone/internet/cell towers not working',
            'backup_methods': [
                input("  Backup method 1: "),
                input("  Backup method 2: "),
                input("  Backup method 3: ")
            ],
            'physical_message_locations': input("  Physical message locations: "),
            'radio_frequencies': input("  Emergency radio frequencies: "),
            'neighbor_network': input("  Neighbor communication network: ")
        }
        
        # Scenario 4: Child emergency at school
        print("\nScenario 4: Child Emergency at School")
        scenarios['child_school_emergency'] = {
            'description': 'Emergency involving child at school',
            'school_notification_protocol': input("  School notification protocol: "),
            'pickup_authorization': input("  Who is authorized for pickup: "),
            'backup_pickup_person': input("  Backup pickup person: "),
            'medical_authorization': input("  Medical treatment authorization: "),
            'communication_with_child': input("  How to communicate with child: ")
        }
        
        # Scenario 5: Adult emergency at work
        print("\nScenario 5: Adult Emergency at Work")
        scenarios['adult_work_emergency'] = {
            'description': 'Emergency involving adult at workplace',
            'workplace_notification': input("  Workplace emergency contact: "),
            'family_notification_chain': input("  Family notification chain: "),
            'childcare_activation': input("  Emergency childcare activation: "),
            'work_coverage_plan': input("  Work coverage plan: "),
            'status_update_responsibility': input("  Who provides status updates: ")
        }
        
        return scenarios
    
    def create_technology_backup_plan(self):
        """Create backup plans for technology failures"""
        print("\n6. TECHNOLOGY BACKUP PLANS")
        
        tech_backup = {}
        
        # Communication device backups
        print("\nCommunication Device Backups:")
        tech_backup['devices'] = {
            'landline_available': input("  Landline phone available? (y/n): ").lower() == 'y',
            'satellite_phone': input("  Satellite phone access? (y/n): ").lower() == 'y',
            'two_way_radios': input("  Two-way radios? (y/n): ").lower() == 'y',
            'radio_frequencies': input("  Radio frequencies to monitor: "),
            'backup_power_for_devices': input("  Backup power for devices: ")
        }
        
        # Internet/data backups
        print("\nInternet/Data Backups:")
        tech_backup['internet'] = {
            'mobile_hotspot': input("  Mobile hotspot available? (y/n): ").lower() == 'y',
            'public_wifi_locations': input("  Known public WiFi locations: "),
            'offline_maps_downloaded': input("  Offline maps downloaded? (y/n): ").lower() == 'y',
            'emergency_app_downloaded': input("  Emergency apps downloaded? (y/n): ").lower() == 'y'
        }
        
        # Information storage backups
        print("\nInformation Storage Backups:")
        tech_backup['information'] = {
            'printed_contact_list': input("  Printed contact list location: "),
            'laminated_cards_in_wallets': input("  Laminated emergency cards in wallets? (y/n): ").lower() == 'y',
            'usb_drive_with_info': input("  USB drive with emergency info? (y/n): ").lower() == 'y',
            'cloud_storage_backup': input("  Cloud storage backup location: "),
            'physical_document_location': input("  Physical document storage location: ")
        }
        
        return tech_backup
    
    def generate_emergency_contact_cards(self):
        """Generate printable emergency contact cards"""
        cards = {}
        
        # Wallet-sized card for each family member
        for member in self.family_info['members']:
            card_info = {
                'name': member['name'],
                'emergency_contacts': [
                    f"Out-of-State: {self.contacts['out_of_state_primary']['name']} - {self.contacts['out_of_state_primary']['phone']}",
                    f"Local 1: {self.contacts['local'][0]['name']} - {self.contacts['local'][0]['phone']}" if self.contacts['local'] else "",
                    f"Local 2: {self.contacts['local'][1]['name']} - {self.contacts['local'][1]['phone']}" if len(self.contacts['local']) > 1 else ""
                ],
                'meeting_points': [
                    f"Primary: {self.communication_plan['meeting_points']['primary']['name']} - {self.communication_plan['meeting_points']['primary']['address']}",
                    f"Secondary: {self.communication_plan['meeting_points']['secondary']['name']} - {self.communication_plan['meeting_points']['secondary']['address']}"
                ],
                'medical_info': {
                    'conditions': member['medical_conditions'],
                    'medications': member['medications'],
                    'doctor': self.contacts['services']['family_doctor']['name'] + " - " + self.contacts['services']['family_doctor']['phone']
                },
                'ice_contact': f"ICE: {self.contacts['out_of_state_primary']['name']} - {self.contacts['out_of_state_primary']['phone']}"
            }
            cards[member['name']] = card_info
        
        return cards
    
    def create_home_information_sheet(self):
        """Create comprehensive home information sheet"""
        home_info = {
            'family_information': self.family_info,
            'emergency_contacts': self.contacts,
            'meeting_points': self.communication_plan['meeting_points'],
            'communication_protocols': self.communication_plan['protocols'],
            'utility_shutoffs': {
                'gas_shutoff_location': input("Gas shutoff valve location: "),
                'water_shutoff_location': input("Water shutoff valve location: "),
                'electrical_panel_location': input("Electrical panel location: "),
                'gas_shutoff_tool_location': input("Gas shutoff tool location: ")
            },
            'important_documents': {
                'safe_location': input("Important documents safe location: "),
                'backup_location': input("Document backup location: "),
                'key_holder': input("Who has access keys: "),
                'digital_copies_location': input("Digital copies stored where: ")
            },
            'emergency_supplies': {
                'kit_location': input("Emergency kit location: "),
                'backup_kit_location': input("Backup kit location: "),
                'car_kit_location': input("Car emergency kit location: "),
                'last_updated': input("Last supply check date: ")
            }
        }
        
        return home_info
    
    def generate_communication_plan(self):
        """Generate complete communication plan"""
        print("Generating comprehensive communication plan...")
        
        # Collect all information
        family_info = self.collect_family_information()
        contacts = self.collect_emergency_contacts()
        meeting_points = self.establish_meeting_points()
        protocols = self.create_communication_protocols()
        scenarios = self.create_scenario_specific_plans()
        tech_backup = self.create_technology_backup_plan()
        
        # Store in communication plan
        self.communication_plan = {
            'family_info': family_info,
            'contacts': contacts,
            'meeting_points': meeting_points,
            'protocols': protocols,
            'scenarios': scenarios,
            'tech_backup': tech_backup
        }
        
        # Generate additional materials
        contact_cards = self.generate_emergency_contact_cards()
        home_info_sheet = self.create_home_information_sheet()
        
        return {
            'communication_plan': self.communication_plan,
            'contact_cards': contact_cards,
            'home_info_sheet': home_info_sheet
        }
    
    def save_communication_plan(self, plan_data):
        """Save communication plan to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main plan
        main_filename = f"family_communication_plan_{timestamp}.json"
        with open(main_filename, 'w') as f:
            json.dump(plan_data, f, indent=2)
        
        # Save contact cards as separate file
        cards_filename = f"emergency_contact_cards_{timestamp}.json"
        with open(cards_filename, 'w') as f:
            json.dump(plan_data['contact_cards'], f, indent=2)
        
        # Create printable text version
        text_filename = f"communication_plan_printable_{timestamp}.txt"
        self.create_printable_version(plan_data, text_filename)
        
        return main_filename, cards_filename, text_filename
    
    def create_printable_version(self, plan_data, filename):
        """Create printable text version of communication plan"""
        with open(filename, 'w') as f:
            f.write("FAMILY EMERGENCY COMMUNICATION PLAN\n")
            f.write("=" * 50 + "\n\n")
            
            # Family information
            f.write("FAMILY INFORMATION\n")
            f.write("-" * 20 + "\n")
            family = plan_data['communication_plan']['family_info']
            f.write(f"Family Name: {family['family_name']}\n")
            f.write(f"Home Address: {family['home_address']}\n")
            f.write(f"Home Phone: {family['home_phone']}\n\n")
            
            f.write("Family Members:\n")
            for member in family['members']:
                f.write(f"  {member['name']} (Age {member['age']})\n")
                f.write(f"    Cell: {member['cell_phone']}\n")
                f.write(f"    Email: {member['email']}\n")
                f.write(f"    Work/School: {member['work_school']}\n")
                if member['medical_conditions']:
                    f.write(f"    Medical: {member['medical_conditions']}\n")
                f.write("\n")
            
            # Emergency contacts
            f.write("EMERGENCY CONTACTS\n")
            f.write("-" * 20 + "\n")
            contacts = plan_data['communication_plan']['contacts']
            
            f.write("Out-of-State Primary Contact:\n")
            oos = contacts['out_of_state_primary']
            f.write(f"  {oos['name']} ({oos['relationship']})\n")
            f.write(f"  Phone: {oos['phone']}\n")
            f.write(f"  Email: {oos['email']}\n")
            f.write(f"  Address: {oos['address']}\n\n")
            
            f.write("Local Emergency Contacts:\n")
            for i, contact in enumerate(contacts['local'], 1):
                f.write(f"  {i}. {contact['name']} ({contact['relationship']})\n")
                f.write(f"     Phone: {contact['phone']}\n")
                f.write(f"     Address: {contact['address']}\n")
                if contact['has_key']:
                    f.write("     Has house key\n")
                if contact['can_pick_up_children']:
                    f.write("     Authorized for child pickup\n")
                f.write("\n")
            
            # Meeting points
            f.write("MEETING POINTS\n")
            f.write("-" * 20 + "\n")
            meeting_points = plan_data['communication_plan']['meeting_points']
            
            for point_type, point_info in meeting_points.items():
                f.write(f"{point_type.title()} Meeting Point:\n")
                f.write(f"  Location: {point_info['name']}\n")
                f.write(f"  Address: {point_info['address']}\n")
                f.write(f"  Phone: {point_info['phone']}\n\n")
            
            # Communication protocols
            f.write("COMMUNICATION PROTOCOLS\n")
            f.write("-" * 20 + "\n")
            protocols = plan_data['communication_plan']['protocols']
            
            f.write("Primary Communication Methods:\n")
            for i, method in enumerate(protocols['primary_methods'], 1):
                f.write(f"  {i}. {method}\n")
            f.write("\n")
            
            f.write("Check-in Schedule:\n")
            f.write(f"  Normal frequency: {protocols['check_in']['frequency_normal']}\n")
            f.write(f"  Emergency frequency: {protocols['check_in']['frequency_emergency']}\n")
            f.write(f"  Check-in times: {protocols['check_in']['check_in_times']}\n\n")
            
            # Emergency scenarios
            f.write("EMERGENCY SCENARIOS\n")
            f.write("-" * 20 + "\n")
            scenarios = plan_data['communication_plan']['scenarios']
            
            for scenario_name, scenario_info in scenarios.items():
                f.write(f"{scenario_name.replace('_', ' ').title()}:\n")
                f.write(f"  Description: {scenario_info['description']}\n")
                if 'immediate_actions' in scenario_info:
                    f.write("  Immediate Actions:\n")
                    for action in scenario_info['immediate_actions']:
                        if action:
                            f.write(f"    - {action}\n")
                f.write("\n")
    
    def display_plan_summary(self, plan_data):
        """Display summary of communication plan"""
        print("\n" + "="*60)
        print("FAMILY COMMUNICATION PLAN SUMMARY")
        print("="*60)
        
        family = plan_data['communication_plan']['family_info']
        print(f"\nFamily: {family['family_name']}")
        print(f"Members: {len(family['members'])}")
        
        contacts = plan_data['communication_plan']['contacts']
        print(f"\nEmergency Contacts:")
        print(f"  Out-of-state: {contacts['out_of_state_primary']['name']}")
        print(f"  Local contacts: {len(contacts['local'])}")
        
        meeting_points = plan_data['communication_plan']['meeting_points']
        print(f"\nMeeting Points:")
        print(f"  Primary: {meeting_points['primary']['name']}")
        print(f"  Secondary: {meeting_points['secondary']['name']}")
        print(f"  Evacuation: {meeting_points['evacuation']['name']}")
        
        scenarios = plan_data['communication_plan']['scenarios']
        print(f"\nScenario Plans: {len(scenarios)} scenarios covered")
        
        print(f"\nContact Cards: Generated for {len(plan_data['contact_cards'])} family members")
        
        print("\nRECOMMENDED NEXT STEPS:")
        print("  • Print and laminate emergency contact cards")
        print("  • Post home information sheet in visible location")
        print("  • Practice communication scenarios with family")
        print("  • Review and update plan every 6 months")
        print("  • Share plan with emergency contacts")
    
    def run_communication_planning(self):
        """Run complete communication planning process"""
        print("Starting family communication emergency planning...\n")
        
        # Generate complete plan
        plan_data = self.generate_communication_plan()
        
        # Save plan files
        print("\nSaving communication plan files...")
        main_file, cards_file, text_file = self.save_communication_plan(plan_data)
        
        # Display summary
        self.display_plan_summary(plan_data)
        
        print(f"\nFiles created:")
        print(f"  • Main plan: {main_file}")
        print(f"  • Contact cards: {cards_file}")
        print(f"  • Printable version: {text_file}")
        
        return plan_data

def main():
    """Main function to run communication planning"""
    planner = CommunicationEmergencyPlan()
    plan = planner.run_communication_planning()
    return plan

if __name__ == "__main__":
    main()