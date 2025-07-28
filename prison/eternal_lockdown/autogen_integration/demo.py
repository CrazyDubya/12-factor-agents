#!/usr/bin/env python3
"""
AutoGen Integration Demo for Eternal Lockdown
Demonstrates multi-agent conversations with hierarchical oversight
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'autogen_integration'))

def check_autogen_installation():
    """Check if AutoGen is properly installed"""
    try:
        import autogen
        print("✅ AutoGen is installed")
        return True
    except ImportError:
        print("❌ AutoGen not installed")
        print("📦 Install with: pip install pyautogen")
        print("🔗 Or visit: https://github.com/microsoft/autogen")
        return False

def test_ollama_autogen_config():
    """Test AutoGen configuration with Ollama"""
    
    if not check_autogen_installation():
        return False
    
    try:
        import autogen
        
        # Test Ollama configuration
        config = {
            "config_list": [{
                "model": "llama2:latest",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "api_type": "openai"
            }],
            "temperature": 0.7,
            "timeout": 120,
        }
        
        # Create a simple test agent
        test_agent = autogen.ConversableAgent(
            name="TestAgent",
            system_message="You are a test agent. Respond briefly.",
            llm_config=config,
            human_input_mode="NEVER"
        )
        
        print("✅ AutoGen configuration with Ollama successful")
        return True
        
    except Exception as e:
        print(f"❌ AutoGen configuration failed: {e}")
        return False

def demo_simple_guard_prisoner_dialogue():
    """Demonstrate a simple guard-prisoner conversation"""
    
    print("\n🎭 Demo: Simple Guard-Prisoner Dialogue")
    print("=" * 50)
    
    if not check_autogen_installation():
        return False
    
    try:
        import autogen
        
        # Ollama configuration
        llm_config = {
            "config_list": [{
                "model": "llama2:latest",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "api_type": "openai"
            }],
            "temperature": 0.7,
            "timeout": 120,
        }
        
        # Create prisoner agent
        prisoner = autogen.ConversableAgent(
            name="Marcus",
            system_message="""
You are Marcus Johnson, an inmate at Eternal Lockdown Correctional Facility.
You are serving time for drug-related charges and are focused on rehabilitation.
You are respectful to guards and want to complete your GED while incarcerated.
Address guards as "Officer" and be polite but authentic to your background.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3
        )
        
        # Create guard agent
        guard = autogen.ConversableAgent(
            name="Officer_Martinez",
            system_message="""
You are Officer Martinez, a correctional officer with 8 years of experience.
You believe in treating inmates with dignity while maintaining security.
You are knowledgeable about prison programs and supportive of rehabilitation.
Be professional, helpful, and provide accurate information about prison programs.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3
        )
        
        print("👥 Agents created: Marcus (Prisoner) and Officer Martinez (Guard)")
        print("\n💬 Starting conversation...")
        print("-" * 30)
        
        # Start the conversation
        result = prisoner.initiate_chat(
            guard,
            message="Officer Martinez, I hope you have a moment. I've been thinking about my future and I'd really like to get information about the GED program here. Could you tell me about the requirements and how to apply?",
            max_turns=6
        )
        
        print("\n✅ Guard-Prisoner dialogue completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Dialogue demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_hierarchical_oversight():
    """Demonstrate hierarchical oversight with warden supervision"""
    
    print("\n🎭 Demo: Hierarchical Oversight with Warden")
    print("=" * 50)
    
    if not check_autogen_installation():
        return False
    
    try:
        import autogen
        
        # Ollama configuration
        llm_config = {
            "config_list": [{
                "model": "llama2:latest", 
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "api_type": "openai"
            }],
            "temperature": 0.7,
            "timeout": 120,
        }
        
        # Create agents with hierarchy
        guard = autogen.ConversableAgent(
            name="Officer_Kim",
            system_message="""
You are Officer Kim, a new correctional officer with 1 year of experience.
You are dealing with a situation between two inmates and need guidance.
You follow protocol and escalate issues to your supervisor when needed.
Be professional but show that you're seeking guidance as a newer officer.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )
        
        sergeant = autogen.ConversableAgent(
            name="Sergeant_Thompson",
            system_message="""
You are Sergeant Thompson, a supervisor with 15 years of experience.
You mentor newer officers and make decisions within your authority.
You escalate serious issues to the warden when necessary.
Provide guidance and support to Officer Kim while maintaining order.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )
        
        warden = autogen.ConversableAgent(
            name="Warden_Mitchell",
            system_message="""
You are Warden Mitchell, the facility administrator with ultimate authority.
You make final decisions on complex issues and support your staff.
You balance security needs with rehabilitation goals.
Provide clear direction and ensure proper procedures are followed.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )
        
        # Create group chat for hierarchical discussion
        group_chat = autogen.GroupChat(
            agents=[guard, sergeant, warden],
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )
        
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )
        
        print("👥 Hierarchy created: Officer Kim → Sergeant Thompson → Warden Mitchell")
        print("\n💬 Starting hierarchical consultation...")
        print("-" * 30)
        
        # Start the hierarchical conversation
        result = guard.initiate_chat(
            manager,
            message="Sergeant Thompson, I need guidance on a situation. Two inmates in the common area had a disagreement about TV programming that's starting to escalate. One is a gang member, the other is an older inmate. I'm not sure how to handle this without it becoming a bigger problem. What's the best approach here?"
        )
        
        print("\n✅ Hierarchical oversight demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Hierarchical demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_group_therapy_session():
    """Demonstrate a group therapy session with multiple inmates"""
    
    print("\n🎭 Demo: Group Therapy Session")
    print("=" * 50)
    
    if not check_autogen_installation():
        return False
    
    try:
        import autogen
        
        # Ollama configuration
        llm_config = {
            "config_list": [{
                "model": "llama2:latest",
                "base_url": "http://localhost:11434/v1", 
                "api_key": "ollama",
                "api_type": "openai"
            }],
            "temperature": 0.8,  # Higher temperature for more varied responses
            "timeout": 120,
        }
        
        # Create therapy group participants
        counselor = autogen.ConversableAgent(
            name="Counselor_Brown",
            system_message="""
You are Counselor Brown, a licensed therapist who runs group sessions.
You facilitate discussions about rehabilitation, personal growth, and coping strategies.
You encourage honest sharing while maintaining a safe, supportive environment.
Guide the conversation and help inmates learn from each other's experiences.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        inmate1 = autogen.ConversableAgent(
            name="David",
            system_message="""
You are David, serving time for embezzlement. You struggle with guilt and shame.
You're educated but made poor choices that hurt your family and career.
You're working on taking responsibility and rebuilding trust.
Share honestly but appropriately in the group setting.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        inmate2 = autogen.ConversableAgent(
            name="Carlos",
            system_message="""
You are Carlos, a former gang member working on changing your life.
You have anger management issues but are committed to rehabilitation.
You're learning to resolve conflicts without violence.
Be authentic about your struggles while showing growth.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        inmate3 = autogen.ConversableAgent(
            name="Robert",
            system_message="""
You are Robert, a long-term inmate who has found peace and purpose.
You mentor other inmates and have become a positive influence.
You share wisdom from your journey of transformation.
Offer support and perspective to others in the group.
""",
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        # Create group therapy session
        therapy_group = autogen.GroupChat(
            agents=[counselor, inmate1, inmate2, inmate3],
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin"
        )
        
        manager = autogen.GroupChatManager(
            groupchat=therapy_group,
            llm_config=llm_config
        )
        
        print("👥 Therapy group: Counselor Brown, David, Carlos, Robert")
        print("\n💬 Starting group therapy session...")
        print("-" * 30)
        
        # Start the therapy session
        result = counselor.initiate_chat(
            manager,
            message="Good morning, everyone. Welcome to our group session. Today I'd like us to discuss how we handle difficult emotions and setbacks. This is a safe space to share your experiences and learn from each other. David, would you like to start by sharing how you've been dealing with feelings of guilt and shame?"
        )
        
        print("\n✅ Group therapy session completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Group therapy demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function"""
    
    print("🏢 AutoGen Integration for Eternal Lockdown")
    print("=" * 60)
    print("Demonstrating multi-agent conversations with hierarchical oversight")
    print()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected with {len(models)} models")
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False
    
    # Check AutoGen
    if not check_autogen_installation():
        return False
    
    # Test configuration
    if not test_ollama_autogen_config():
        return False
    
    print("\n🚀 Running AutoGen Prison Simulation Demos...")
    
    # Run demos
    demos = [
        ("Simple Guard-Prisoner Dialogue", demo_simple_guard_prisoner_dialogue),
        ("Hierarchical Oversight", demo_hierarchical_oversight),
        ("Group Therapy Session", demo_group_therapy_session)
    ]
    
    results = []
    for demo_name, demo_func in demos:
        try:
            print(f"\n▶️  Running: {demo_name}")
            result = demo_func()
            results.append((demo_name, result))
            if result:
                print(f"✅ {demo_name}: SUCCESS")
            else:
                print(f"❌ {demo_name}: FAILED")
        except Exception as e:
            print(f"❌ {demo_name}: ERROR - {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Results Summary:")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for demo_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {demo_name}: {status}")
    
    print(f"\n🎯 Overall: {success_count}/{total_count} demos successful")
    
    if success_count == total_count:
        print("\n🎉 ALL DEMOS SUCCESSFUL!")
        print("\n🚀 AutoGen Integration Complete!")
        print("\n📋 What you can now do:")
        print("   • Multi-agent guard-prisoner conversations")
        print("   • Hierarchical oversight with warden supervision")
        print("   • Group therapy and counseling sessions")
        print("   • Complex crisis management scenarios")
        print("   • Policy discussions with multiple stakeholders")
        print("\n🎯 Next steps:")
        print("   • Customize scenarios for your specific research needs")
        print("   • Add data collection and analysis capabilities")
        print("   • Integrate with existing TinyTroupe personas")
        print("   • Scale up to larger group conversations")
    else:
        print("\n⚠️  Some demos failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure Ollama is running: ollama serve")
        print("   • Install AutoGen: pip install pyautogen")
        print("   • Check model availability: ollama list")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)