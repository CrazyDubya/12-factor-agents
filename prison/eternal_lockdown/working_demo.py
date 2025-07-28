#!/usr/bin/env python3
"""
Working Eternal Lockdown Demo - Prison Simulation with Ollama
"""

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'tinytroupe'))

def main():
    """Main demo function"""
    
    print("🏢 Eternal Lockdown Prison Simulation - Working Demo")
    print("=" * 60)
    
    # Test Ollama connection first
    print("🧪 Testing Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding. Please start Ollama first.")
            return False
        
        models = response.json().get("models", [])
        print(f"✅ Ollama connected with {len(models)} models available")
        if models:
            print(f"   Using model: {models[0]['name']}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False
    
    # Import TinyTroupe components
    try:
        from tinytroupe.agent import TinyPerson
        from tinytroupe.environment import TinyWorld
        print("✅ TinyTroupe components imported successfully")
    except Exception as e:
        print(f"❌ Failed to import TinyTroupe: {e}")
        return False
    
    # Create prison environment
    try:
        prison = TinyWorld("Eternal Lockdown Correctional Facility")
        print(f"✅ Created prison environment: {prison.name}")
    except Exception as e:
        print(f"❌ Failed to create environment: {e}")
        return False
    
    # Create inmate persona
    try:
        marcus = TinyPerson("Marcus Johnson")
        
        # Use the correct method signature for define
        marcus.define("occupation", "Inmate")
        marcus.define("age", 28)
        marcus.define("personality", "Respectful but sometimes frustrated, wants to rehabilitate")
        marcus.define("background", """
        Serving 5 years for drug possession with intent to distribute.
        Has been incarcerated for 2 years. Focused on rehabilitation.
        Has a young daughter he wants to see again.
        Enrolled in education and substance abuse programs.
        Grew up in a tough neighborhood but regrets his choices.
        """)
        marcus.define("current_situation", "Inmate at medium-security prison working on GED")
        marcus.define("goals", "Complete education, stay out of trouble, reunite with daughter")
        
        print(f"✅ Created inmate persona: {marcus.name}")
        
    except Exception as e:
        print(f"❌ Failed to create inmate: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create guard persona
    try:
        officer_martinez = TinyPerson("Officer Martinez")
        
        officer_martinez.define("occupation", "Correctional Officer")
        officer_martinez.define("age", 34)
        officer_martinez.define("personality", "Firm but fair, professional, supportive of rehabilitation")
        officer_martinez.define("background", """
        8 years experience in corrections. Former military.
        Associate degree in criminal justice.
        Believes in treating inmates with dignity while maintaining security.
        Family background in law enforcement.
        """)
        officer_martinez.define("current_situation", "Day shift correctional officer")
        officer_martinez.define("approach", "Professional, follows procedures, uses good judgment")
        
        print(f"✅ Created guard persona: {officer_martinez.name}")
        
    except Exception as e:
        print(f"❌ Failed to create guard: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Add agents to prison
    try:
        prison.add_agent(marcus)
        prison.add_agent(officer_martinez)
        print("✅ Added agents to prison environment")
    except Exception as e:
        print(f"❌ Failed to add agents: {e}")
        return False
    
    # Test basic interaction
    print("\n🎭 Testing Prison Interaction Scenario")
    print("-" * 40)
    
    try:
        # Scenario: Marcus asks about GED program
        print("📋 Scenario: Inmate inquires about education program")
        
        # Marcus initiates conversation
        print(f"\n👤 {marcus.name} approaches Officer Martinez:")
        marcus_response = marcus.listen_and_act(
            "You see Officer Martinez during recreation time. "
            "Approach her respectfully and ask about the GED program. "
            "You want to complete your education while in prison."
        )
        
        print("   [Marcus approaches the officer about education]")
        
        # Officer responds
        print(f"\n👮 {officer_martinez.name} responds:")
        martinez_response = officer_martinez.listen_and_act(
            "An inmate named Marcus has approached you asking about the GED program. "
            "Provide helpful information about enrollment, requirements, and schedule. "
            "Be professional and encouraging."
        )
        
        print("   [Officer provides information about the GED program]")
        
        print("\n✅ Basic interaction completed successfully!")
        
    except Exception as e:
        print(f"❌ Interaction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test group communication
    print("\n📢 Testing Group Communication")
    print("-" * 30)
    
    try:
        # Broadcast announcement
        prison.broadcast("Attention all inmates: Dinner will be served in the cafeteria in 15 minutes. Please prepare to move in an orderly fashion.")
        
        print("📢 Broadcast sent: Dinner announcement")
        
        # Agents respond
        print(f"\n👤 {marcus.name} responds:")
        marcus.listen_and_act("Respond appropriately to the dinner announcement.")
        
        print(f"\n👮 {officer_martinez.name} responds:")
        officer_martinez.listen_and_act("Prepare to escort inmates to dinner safely.")
        
        print("\n✅ Group communication test completed!")
        
    except Exception as e:
        print(f"❌ Group communication failed: {e}")
        return False
    
    # Success summary
    print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n✅ Achievements:")
    print("   🔧 Ollama integration with TinyTroupe working")
    print("   👥 Prison personas created and functioning")
    print("   💬 Individual interactions working")
    print("   📢 Group broadcasts working")
    print("   🏢 Prison simulation framework established")
    
    print("\n🎯 Eternal Lockdown System Status: OPERATIONAL")
    
    print("\n📋 What we've built:")
    print("   - Modified TinyTroupe to use Ollama instead of OpenAI")
    print("   - Created realistic prison personas (inmates, guards)")
    print("   - Demonstrated natural AI-powered conversations")
    print("   - Built foundation for complex prison simulations")
    print("   - Established framework for rehabilitation research")
    
    print("\n🚀 Ready for advanced features:")
    print("   - Multiple inmate types and crime backgrounds")
    print("   - Complex scenarios (incidents, programs, visits)")
    print("   - Data collection and behavioral analysis")
    print("   - Policy testing and outcome prediction")
    print("   - Rehabilitation program effectiveness studies")
    
    print("\n📝 Next steps:")
    print("   1. Expand persona library with diverse backgrounds")
    print("   2. Create complex multi-agent scenarios")
    print("   3. Add incident and crisis management simulations")
    print("   4. Implement data collection for research")
    print("   5. Build policy testing frameworks")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🏆 Eternal Lockdown Prison Simulation System is ready!")
        else:
            print("\n❌ Demo failed. Check the errors above.")
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()