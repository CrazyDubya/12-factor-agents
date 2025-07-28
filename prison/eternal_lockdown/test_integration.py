#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Eternal Lockdown
Test all systems before full simulation run
"""

import sys
import os
import traceback

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from core.game_theory import GameTheoryEngine, Strategy, PrisonersDilemma
        print("   ✅ Game theory imports")
        
        from core.agents import Agent, Prisoner, Guard, PersonalityType, IntelligenceLevel
        print("   ✅ Agent imports")
        
        from persistence import SimulationPersistence
        print("   ✅ Persistence imports")
        
        from sentence_system import SentenceCalculator, SentenceInfo
        print("   ✅ Sentence system imports")
        
        from emotional_system import EmotionalProfile, EmotionalDecisionEngine, PrivilegeType
        print("   ✅ Emotional system imports")
        
        from personality_system import PersonalityGenerator, DeepPersonality
        print("   ✅ Personality system imports")
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_basic_systems():
    """Test basic system functionality"""
    print("\n🧪 Testing basic systems...")
    
    try:
        # Test game theory
        from core.game_theory import PrisonersDilemma, Strategy
        pd = PrisonersDilemma()
        payoffs = pd.play_round(Strategy.COOPERATE, Strategy.DEFECT)
        assert payoffs == (0.0, 5.0), f"Expected (0.0, 5.0), got {payoffs}"
        print("   ✅ Game theory working")
        
        # Test sentence system
        from sentence_system import SentenceCalculator
        calc = SentenceCalculator()
        sentence = calc.calculate_sentence("drug possession")
        assert 3 <= sentence.actual_days <= 30, f"Sentence {sentence.actual_days} not in range 3-30"
        print("   ✅ Sentence system working")
        
        # Test emotional system
        from emotional_system import EmotionalProfile, EmotionalDecisionEngine
        profile = EmotionalProfile()
        engine = EmotionalDecisionEngine()
        modifier = engine.calculate_emotional_cooperation_modifier(profile, 10)
        assert -0.5 <= modifier <= 0.5, f"Modifier {modifier} out of range"
        print("   ✅ Emotional system working")
        
        # Test personality system
        from personality_system import PersonalityGenerator
        gen = PersonalityGenerator()
        personality = gen.generate_personality("Test", "drug possession")
        assert personality.history.background_type is not None
        print("   ✅ Personality system working")
        
        return True
    except Exception as e:
        print(f"   ❌ System error: {e}")
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test agent creation with all systems"""
    print("\n🧪 Testing agent creation...")
    
    try:
        from core.agents import Prisoner, Guard, PersonalityType, IntelligenceLevel
        
        # Test prisoner creation
        prisoner = Prisoner(
            1, "Test Prisoner", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM,
            crime="drug possession", sentence_days=15
        )
        assert prisoner.id == 1
        assert prisoner.crime == "drug possession"
        print("   ✅ Prisoner creation working")
        
        # Test guard creation
        guard = Guard(
            2, "Test Guard", PersonalityType.STRATEGIC, IntelligenceLevel.HIGH,
            rank="Officer", years_experience=5
        )
        assert guard.id == 2
        assert guard.rank == "Officer"
        print("   ✅ Guard creation working")
        
        return True
    except Exception as e:
        print(f"   ❌ Agent creation error: {e}")
        traceback.print_exc()
        return False

def test_social_network():
    """Test social network functionality"""
    print("\n🧪 Testing social network...")
    
    try:
        # Import the SocialNetwork class from run_ollama_simulation
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_ollama_simulation", "run_ollama_simulation.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        network = module.SocialNetwork()
        
        # Test relationship update
        network.update_relationship(1, 2, "mutual_cooperation", (3.0, 3.0))
        key = tuple(sorted([1, 2]))
        assert key in network.relationships
        print("   ✅ Relationship tracking working")
        
        # Test gang formation
        network.form_gang("Test Gang", 1, [2])
        assert "Test Gang" in network.gangs
        assert 1 in network.gangs["Test Gang"]
        print("   ✅ Gang formation working")
        
        return True
    except Exception as e:
        print(f"   ❌ Social network error: {e}")
        traceback.print_exc()
        return False

def test_ollama_decision_engine():
    """Test Ollama decision engine"""
    print("\n🧪 Testing Ollama decision engine...")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_ollama_simulation", "run_ollama_simulation.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        engine = module.OllamaDecisionEngine()
        
        # Test connection (may fail if Ollama not running)
        connection_works = engine.test_connection()
        if connection_works:
            print("   ✅ Ollama connection working")
        else:
            print("   ⚠️  Ollama not connected (will use fallback)")
        
        # Test fallback decision making
        from core.agents import Prisoner, PersonalityType, IntelligenceLevel
        from emotional_system import EmotionalProfile
        
        agent = Prisoner(1, "Test", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM, crime="test")
        network = module.SocialNetwork()
        emotion = EmotionalProfile()
        
        decision, reasoning = engine._personality_decision_with_context(agent, 2, network)
        assert decision in [module.Strategy.COOPERATE, module.Strategy.DEFECT]
        print("   ✅ Fallback decision making working")
        
        return True
    except Exception as e:
        print(f"   ❌ Ollama engine error: {e}")
        traceback.print_exc()
        return False

def test_persistence():
    """Test persistence system"""
    print("\n🧪 Testing persistence...")
    
    try:
        from persistence import SimulationPersistence
        from core.agents import Prisoner, PersonalityType, IntelligenceLevel
        
        persistence = SimulationPersistence(save_dir="test_saves")
        
        # Create test data
        agents = [Prisoner(1, "Test", PersonalityType.COOPERATIVE, IntelligenceLevel.MEDIUM, crime="test")]
        
        # Test save (create minimal social network)
        class MockSocialNetwork:
            def __init__(self):
                self.relationships = {}
                self.gangs = {}
                self.alliances = {}
                self.enemies = {}
                self.influence_scores = {}
        
        network = MockSocialNetwork()
        stats = {"test": "data"}
        metadata = {"test": True}
        
        timestamp = persistence.auto_save(agents, network, stats, metadata)
        assert timestamp is not None
        print("   ✅ Auto-save working")
        
        # Test load
        data = persistence.auto_load()
        assert data is not None
        assert "agents" in data
        print("   ✅ Auto-load working")
        
        # Cleanup
        import shutil
        if os.path.exists("test_saves"):
            shutil.rmtree("test_saves")
        
        return True
    except Exception as e:
        print(f"   ❌ Persistence error: {e}")
        traceback.print_exc()
        return False

def test_integration_flow():
    """Test the complete integration flow"""
    print("\n🧪 Testing integration flow...")
    
    try:
        # Import main simulation components
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_ollama_simulation", "run_ollama_simulation.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test agent creation function
        agents = module.create_prison_population()
        assert len(agents) > 0
        print(f"   ✅ Created {len(agents)} agents")
        
        # Test that agents have required attributes
        for agent in agents:
            assert hasattr(agent, 'id')
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'personality')
            assert hasattr(agent, 'ollama_model')
        print("   ✅ Agents have required attributes")
        
        # Test systems initialization
        from emotional_system import EmotionalProfile, EmotionalDecisionEngine
        from sentence_system import SentenceCalculator
        from personality_system import PersonalityGenerator
        
        emotional_engine = EmotionalDecisionEngine()
        sentence_calc = SentenceCalculator()
        personality_gen = PersonalityGenerator()
        
        # Test creating profiles for agents
        agent_emotions = {}
        agent_sentences = {}
        
        for agent in agents[:2]:  # Test first 2 agents
            agent_emotions[agent.id] = EmotionalProfile()
            if hasattr(agent, 'crime'):
                sentence_info = sentence_calc.calculate_sentence(agent.crime)
                agent_sentences[agent.id] = sentence_info
        
        print("   ✅ Agent profiles created successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Integration flow error: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 ETERNAL LOCKDOWN - COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Basic Systems", test_basic_systems),
        ("Agent Creation", test_agent_creation),
        ("Social Network", test_social_network),
        ("Ollama Engine", test_ollama_decision_engine),
        ("Persistence", test_persistence),
        ("Integration Flow", test_integration_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:20}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System ready for full simulation!")
        print("✅ You can safely run: python3 run_ollama_simulation.py")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Check errors above before running simulation.")
        print("🔧 Fix issues then re-run tests.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        traceback.print_exc()
        exit(1)