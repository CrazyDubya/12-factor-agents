#!/usr/bin/env python3
"""
Test script to verify PROPER multi-framework integration
Tests each framework individually and then together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ollama_connection():
    """Test Ollama connection"""
    print("🔧 Testing Ollama Connection...")
    try:
        from ollama_utils import OllamaClient
        client = OllamaClient()
        
        # Test basic message
        response = client.send_message([
            {"role": "user", "content": "Say 'Ollama is working' if you can understand this."}
        ])
        
        if "working" in response.get("choices", [{}])[0].get("message", {}).get("content", "").lower():
            print("✅ Ollama connection successful")
            return True
        else:
            print("❌ Ollama response unexpected")
            return False
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_tinytroupe_integration():
    """Test TinyTroupe with Ollama"""
    print("\n🤖 Testing TinyTroupe Integration...")
    try:
        # Setup Ollama for TinyTroupe
        from ollama_utils import setup_ollama_for_tinytroupe
        setup_ollama_for_tinytroupe()
        
        # Import TinyTroupe components
        from tinytroupe.environment import TinyWorld
        from tinytroupe.agent import TinyPerson
        
        # Create a simple test world
        test_world = TinyWorld("Test Prison")
        
        # Create a test agent
        test_inmate = TinyPerson("Test Inmate")
        test_inmate.define("personality", "Cooperative and helpful")
        
        # Add agent to world
        test_world.add_agent(test_inmate)
        
        print("✅ TinyTroupe integration successful")
        return True
        
    except Exception as e:
        print(f"❌ TinyTroupe integration failed: {e}")
        return False

def test_autogen_integration():
    """Test AutoGen integration"""
    print("\n👮 Testing AutoGen Integration...")
    try:
        # Test direct AutoGen import first
        import autogen
        print(f"✅ AutoGen {autogen.__version__} is installed")
        
        # Test our integration
        from autogen_integration.demo import test_autogen_installation
        result = test_autogen_installation()
        if result:
            print("✅ AutoGen integration successful")
            return True
        else:
            print("❌ AutoGen integration failed")
            return False
            
    except ImportError as e:
        print(f"❌ AutoGen not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ AutoGen integration failed: {e}")
        return False

def test_crewai_integration():
    """Test CrewAI integration"""
    print("\n🔧 Testing CrewAI Integration...")
    try:
        from crewai_integration import CREWAI_AVAILABLE
        if CREWAI_AVAILABLE:
            from crewai_integration import PrisonCrewAI
            crew_system = PrisonCrewAI()
            print("✅ CrewAI integration successful")
            return True
        else:
            print("❌ CrewAI not available - install with: pip install crewai")
            return False
            
    except Exception as e:
        print(f"❌ CrewAI integration failed: {e}")
        return False

def test_multi_framework_orchestrator():
    """Test the complete orchestrator"""
    print("\n🎭 Testing Multi-Framework Orchestrator...")
    try:
        from multi_framework_orchestrator import MultiFrameworkPrisonOrchestrator
        
        # Initialize orchestrator
        orchestrator = MultiFrameworkPrisonOrchestrator()
        
        print("✅ Multi-framework orchestrator successful")
        return True
        
    except Exception as e:
        print(f"❌ Multi-framework orchestrator failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 PROPER MULTI-FRAMEWORK INTEGRATION TESTS")
    print("=" * 60)
    print("Testing the ACTUAL frameworks as requested in DOTHIS.md")
    print()
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("TinyTroupe Integration", test_tinytroupe_integration),
        ("AutoGen Integration", test_autogen_integration),
        ("CrewAI Integration", test_crewai_integration),
        ("Multi-Framework Orchestrator", test_multi_framework_orchestrator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🏆 ALL TESTS PASSED!")
        print("✅ Ready to run proper multi-framework simulation")
        print("✅ Using ACTUAL TinyTroupe, AutoGen, and CrewAI")
        print("✅ No more amateur substitutes!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("🔧 Fix the failing components before running simulation")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Install missing packages: pip install -r requirements.txt")
        print("3. Install AutoGen: pip install pyautogen")
        print("4. Install CrewAI: pip install crewai")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)