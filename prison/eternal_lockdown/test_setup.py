#!/usr/bin/env python3
"""
Quick test to verify Eternal Lockdown setup is working
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'tinytroupe'))

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🧪 Testing Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected. Available models:")
            for model in models[:5]:  # Show first 5 models
                print(f"   - {model['name']}")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_ollama_client():
    """Test our Ollama client wrapper"""
    print("\n🔧 Testing Ollama client wrapper...")
    
    try:
        from ollama_utils import OllamaClient
        print("✅ Successfully imported OllamaClient")
        
        client = OllamaClient(cache_api_calls=False)  # Disable cache for testing
        print("✅ OllamaClient initialized")
        
        # Test a simple message
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in exactly 5 words."}
        ]
        
        print("📤 Sending test message to Ollama...")
        response = client.send_message(test_messages)
        
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"✅ Received response: {content[:100]}...")
            return True
        else:
            print("❌ Invalid response format")
            return False
            
    except Exception as e:
        print(f"❌ Error testing client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_persona_creation():
    """Test creating prison personas"""
    print("\n👥 Testing persona creation...")
    
    try:
        # Test inmate creation
        from personas.inmates import PrisonInmate
        
        test_inmate = PrisonInmate(
            name="Test Inmate",
            crime_type="Test crime",
            sentence_length="1 year",
            age=30
        )
        
        print(f"✅ Created inmate: {test_inmate.name}")
        print(f"   Crime: {test_inmate.crime_type}")
        print(f"   Sentence: {test_inmate.sentence_length}")
        
        # Test guard creation
        from personas.guards import PrisonGuard
        
        test_guard = PrisonGuard(
            name="Test Guard",
            rank="Officer",
            years_experience=5
        )
        
        print(f"✅ Created guard: {test_guard.name}")
        print(f"   Rank: {test_guard.rank}")
        print(f"   Experience: {test_guard.years_experience} years")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating personas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🏢 Eternal Lockdown - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_ollama_connection,
        test_ollama_client,
        test_persona_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    test_names = [
        "Ollama Connection",
        "Ollama Client",
        "Persona Creation"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 All tests passed! Eternal Lockdown is ready to use.")
        print("\n📝 Next steps:")
        print("1. Run: python3 scenarios/daily_routine.py")
        print("2. Explore different scenarios in the scenarios/ directory")
        print("3. Create custom personas and interactions")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check available models: ollama list")
        print("3. Pull a model if needed: ollama pull llama2")
    
    return all_passed

if __name__ == "__main__":
    main()