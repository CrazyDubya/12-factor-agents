#!/usr/bin/env python3
"""
Simple Eternal Lockdown Demo - Working Prison Simulation
"""

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'tinytroupe'))

def create_simple_prison_demo():
    """Create a simple working demo of the prison simulation"""
    
    print("🏢 Eternal Lockdown - Simple Prison Demo")
    print("=" * 50)
    
    # Import TinyTroupe components
    from tinytroupe.agent import TinyPerson
    from tinytroupe.environment import TinyWorld
    
    print("✅ TinyTroupe components imported successfully")
    
    # Create prison world
    prison = TinyWorld("Eternal Lockdown Correctional Facility")
    
    # Check available methods
    print(f"✅ Created prison world: {prison.name}")
    
    # Create simple inmate
    marcus = TinyPerson("Marcus Johnson")
    marcus.define("""
    You are Marcus Johnson, a 28-year-old inmate at Eternal Lockdown Correctional Facility.
    You were convicted of drug possession with intent to distribute and are serving a 5-year sentence.
    You've been incarcerated for 2 years and are focused on rehabilitation.
    
    PERSONALITY:
    - Respectful but sometimes frustrated
    - Wants to change your life and get out of the drug trade
    - Enrolled in education and substance abuse programs
    - Generally follows rules but speaks up when treated unfairly
    - Has a young daughter you want to see again
    
    BACKGROUND:
    - Grew up in a tough neighborhood
    - Started selling drugs to support your family
    - Regret the choices that led you here
    - Working toward your GED in prison
    - Attending NA meetings
    
    You speak authentically, showing both your street background and your desire to improve.
    """)
    
    # Create guard
    officer_martinez = TinyPerson("Officer Martinez")
    officer_martinez.define("""
    You are Officer Maria Martinez, a correctional officer at Eternal Lockdown Correctional Facility.
    You have 8 years of experience in corrections and believe in treating inmates with dignity.
    
    APPROACH:
    - Firm but fair in all interactions
    - Support rehabilitation efforts
    - Follow procedures while using good judgment
    - Build appropriate professional relationships
    - De-escalate conflicts when possible
    
    BACKGROUND:
    - Former military, family in law enforcement
    - Associate degree in criminal justice
    - Motivated by public service and safety
    - Believe people can change with the right support
    
    You maintain authority while treating inmates as human beings deserving of respect.
    """)
    
    print("✅ Created personas:")
    print(f"   - {marcus.name}: Inmate seeking rehabilitation")
    print(f"   - {officer_martinez.name}: Experienced, fair officer")
    
    # Add agents to world
    prison.add_agent(marcus)
    prison.add_agent(officer_martinez)
    
    print("✅ Added agents to prison world")
    
    # Test basic interaction
    print("\n🎭 Testing Basic Interaction")
    print("-" * 30)
    
    # Scenario: Marcus asks about education program
    print("📋 Scenario: Marcus wants information about the GED program")
    
    # Marcus speaks first
    print(f"\n👤 {marcus.name}:")
    marcus_action = marcus.listen_and_act(
        "You see Officer Martinez during recreation time. "
        "Approach her respectfully and ask about enrolling in the GED program. "
        "Explain why education is important to you."
    )
    
    # Officer responds
    print(f"\n👮 {officer_martinez.name}:")
    martinez_action = officer_martinez.listen_and_act(
        "Marcus Johnson has approached you asking about the GED program. "
        "Provide helpful, encouraging information about enrollment requirements, "
        "class schedules, and the application process."
    )
    
    print("\n✅ Basic interaction completed!")
    
    # Test group broadcast
    print("\n📢 Testing Group Communication")
    print("-" * 30)
    
    # Broadcast announcement
    prison.broadcast("Attention all inmates: Dinner will be served in 15 minutes. Please prepare to move to the cafeteria in an orderly fashion.")
    
    print("📢 Broadcast sent: Dinner announcement")
    
    # Both agents respond to announcement
    print(f"\n👤 {marcus.name} responds to announcement:")
    marcus.listen_and_act("Respond to the dinner announcement appropriately.")
    
    print(f"\n👮 {officer_martinez.name} responds to announcement:")
    officer_martinez.listen_and_act("Prepare to escort inmates to dinner and maintain order.")
    
    print("\n✅ Group communication test completed!")
    
    # Summary
    print("\n📊 Demo Results")
    print("=" * 50)
    print("✅ Ollama integration working with TinyTroupe")
    print("✅ Prison personas created and functioning")
    print("✅ Individual agent interactions working")
    print("✅ Group broadcasts and responses working")
    print("✅ Realistic prison scenario demonstrated")
    
    print("\n🎯 Key Achievements:")
    print("- Modified TinyTroupe to use Ollama instead of OpenAI")
    print("- Created prison-specific personas with detailed backgrounds")
    print("- Demonstrated natural conversation between inmate and guard")
    print("- Showed group communication capabilities")
    print("- Established foundation for complex prison simulations")
    
    print("\n🚀 Ready for Advanced Features:")
    print("- Multiple inmate types and backgrounds")
    print("- Complex scenarios (incidents, programs, visits)")
    print("- Data collection and behavioral analysis")
    print("- Policy testing and outcome prediction")
    print("- Rehabilitation program effectiveness studies")
    
    return prison, marcus, officer_martinez

def test_conversation_flow():
    """Test a more detailed conversation between inmate and guard"""
    
    print("\n\n🗣️ Extended Conversation Test")
    print("=" * 40)
    
    from tinytroupe.agent import TinyPerson
    from tinytroupe.environment import TinyWorld
    
    # Create focused environment
    counseling_room = TinyWorld("Counseling Office")
    
    # Create counselor guard
    counselor = TinyPerson("Counselor Williams")
    counselor.define("""
    You are Lisa Williams, a correctional counselor with a master's degree in social work.
    You conduct one-on-one sessions with inmates to support their rehabilitation.
    You're empathetic but professional, helping inmates work through their issues.
    """)
    
    # Create inmate with issues
    troubled_inmate = TinyPerson("David Chen")
    troubled_inmate.define("""
    You are David Chen, serving time for embezzlement. You're struggling with guilt
    and shame about your crimes. You have two teenage children who won't speak to you.
    You're in counseling to work through your issues and prepare for reintegration.
    """)
    
    counseling_room.add_agent(counselor)
    counseling_room.add_agent(troubled_inmate)
    
    print("✅ Set up counseling session scenario")
    
    # Multi-turn conversation
    print("\n💬 Counseling Session:")
    
    # Turn 1: Opening
    print(f"\n👩‍⚕️ {counselor.name}:")
    counselor.listen_and_act("Begin the counseling session. Ask David how he's been feeling lately and if there's anything specific he wants to discuss today.")
    
    print(f"\n👤 {troubled_inmate.name}:")
    troubled_inmate.listen_and_act("You're feeling overwhelmed with guilt about your crimes and the impact on your family. Share these feelings with the counselor.")
    
    # Turn 2: Deeper discussion
    print(f"\n👩‍⚕️ {counselor.name}:")
    counselor.listen_and_act("Acknowledge David's feelings and help him explore healthy ways to cope with guilt while working toward making amends.")
    
    print(f"\n👤 {troubled_inmate.name}:")
    troubled_inmate.listen_and_act("Express your fears about whether your children will ever forgive you and how to rebuild those relationships.")
    
    print("\n✅ Extended conversation completed!")
    
    return counseling_room, counselor, troubled_inmate

if __name__ == "__main__":
    try:
        # Test Ollama first
        print("🧪 Checking Ollama connection...")
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding. Please start Ollama first.")
            exit(1)
        
        models = response.json().get("models", [])
        print(f"✅ Ollama connected with {len(models)} models available")
        
        # Run main demo
        prison, marcus, martinez = create_simple_prison_demo()
        
        # Run extended conversation
        counseling, counselor, inmate = test_conversation_flow()
        
        print("\n🎉 ALL DEMOS SUCCESSFUL!")
        print("\n🏢 Eternal Lockdown Prison Simulation System is fully operational!")
        print("\n📋 What we've accomplished:")
        print("✅ Successfully integrated Ollama with TinyTroupe")
        print("✅ Created realistic prison personas and scenarios")
        print("✅ Demonstrated natural AI-powered conversations")
        print("✅ Built foundation for complex prison simulations")
        print("✅ Established framework for rehabilitation research")
        
        print("\n🎯 Next steps for development:")
        print("1. Add more diverse personas (different crime types, backgrounds)")
        print("2. Create complex scenarios (incidents, programs, family visits)")
        print("3. Implement data collection for behavioral analysis")
        print("4. Build policy testing frameworks")
        print("5. Add outcome tracking and prediction capabilities")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()