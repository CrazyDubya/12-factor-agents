#!/usr/bin/env python3
"""
Version 2.0 Integration Test
Verify all V2.0 modules integrate correctly with main system
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_v2_module_imports():
    """Test that all V2.0 modules import correctly"""
    print("🧪 Testing V2.0 Module Imports...")
    
    try:
        from v2_modules.cyber_attack_response import CyberAttackResponseModule
        print("✅ CyberAttackResponseModule imported successfully")
    except ImportError as e:
        print(f"❌ CyberAttackResponseModule import failed: {e}")
        return False
    
    try:
        from v2_modules.emp_hardening_module import EMPHardeningModule
        print("✅ EMPHardeningModule imported successfully")
    except ImportError as e:
        print(f"❌ EMPHardeningModule import failed: {e}")
        return False
    
    try:
        from v2_modules.nuclear_safety_module import NuclearSafetyModule
        print("✅ NuclearSafetyModule imported successfully")
    except ImportError as e:
        print(f"❌ NuclearSafetyModule import failed: {e}")
        return False
    
    return True

def test_module_initialization():
    """Test that all V2.0 modules initialize correctly"""
    print("\n🧪 Testing V2.0 Module Initialization...")
    
    try:
        from v2_modules.cyber_attack_response import CyberAttackResponseModule
        cyber_module = CyberAttackResponseModule("test_modern_threats.db")
        print("✅ CyberAttackResponseModule initialized successfully")
    except Exception as e:
        print(f"❌ CyberAttackResponseModule initialization failed: {e}")
        return False
    
    try:
        from v2_modules.emp_hardening_module import EMPHardeningModule
        emp_module = EMPHardeningModule("test_modern_threats.db")
        print("✅ EMPHardeningModule initialized successfully")
    except Exception as e:
        print(f"❌ EMPHardeningModule initialization failed: {e}")
        return False
    
    try:
        from v2_modules.nuclear_safety_module import NuclearSafetyModule
        nuclear_module = NuclearSafetyModule("test_modern_threats.db")
        print("✅ NuclearSafetyModule initialized successfully")
    except Exception as e:
        print(f"❌ NuclearSafetyModule initialization failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of each V2.0 module"""
    print("\n🧪 Testing V2.0 Basic Functionality...")
    
    try:
        # Test Cyber Attack Response
        from v2_modules.cyber_attack_response import CyberAttackResponseModule
        cyber_module = CyberAttackResponseModule("test_modern_threats.db")
        assessment = cyber_module.assess_cyber_preparedness(4)
        assert 'preparedness_score' in assessment
        print("✅ Cyber Attack Response basic functionality works")
        
        # Test EMP Hardening
        from v2_modules.emp_hardening_module import EMPHardeningModule
        emp_module = EMPHardeningModule("test_modern_threats.db")
        vulnerability = emp_module.assess_emp_vulnerability()
        assert 'vulnerability_score' in vulnerability
        print("✅ EMP Hardening basic functionality works")
        
        # Test Nuclear Safety
        from v2_modules.nuclear_safety_module import NuclearSafetyModule
        nuclear_module = NuclearSafetyModule("test_modern_threats.db")
        preparedness = nuclear_module.assess_nuclear_preparedness(20)
        assert 'preparedness_score' in preparedness
        print("✅ Nuclear Safety basic functionality works")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
    
    return True

def test_main_system_integration():
    """Test integration with main preparedness system"""
    print("\n🧪 Testing Main System Integration...")
    
    try:
        from integrated_preparedness_system import IntegratedPreparednessSystem
        system = IntegratedPreparednessSystem("test_preparedness_data")
        
        # Check that V2.0 modules are initialized
        assert hasattr(system, 'cyber_response')
        assert hasattr(system, 'emp_hardening')
        assert hasattr(system, 'nuclear_safety')
        print("✅ V2.0 modules integrated into main system")
        
        # Check module count
        assert system.system_status['modules_active'] == 19
        print("✅ Module count updated correctly (19 modules)")
        
    except Exception as e:
        print(f"❌ Main system integration test failed: {e}")
        return False
    
    return True

def cleanup_test_files():
    """Clean up test database files"""
    test_files = [
        "test_modern_threats.db",
        "test_preparedness_data"
    ]
    
    for file in test_files:
        try:
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                import shutil
                shutil.rmtree(file)
        except:
            pass

def main():
    """Run all V2.0 integration tests"""
    print("🚀 VERSION 2.0 INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("V2.0 Module Imports", test_v2_module_imports),
        ("V2.0 Module Initialization", test_module_initialization),
        ("V2.0 Basic Functionality", test_basic_functionality),
        ("Main System Integration", test_main_system_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Clean up test files
    cleanup_test_files()
    
    print(f"\n{'='*60}")
    print(f"🏆 V2.0 INTEGRATION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL V2.0 INTEGRATION TESTS PASSED!")
        print("🎯 Version 2.0 Phase 2A: Modern Threat Integration is READY")
    else:
        print("❌ Some V2.0 integration tests failed")
        print("🔧 Integration issues need to be resolved")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)