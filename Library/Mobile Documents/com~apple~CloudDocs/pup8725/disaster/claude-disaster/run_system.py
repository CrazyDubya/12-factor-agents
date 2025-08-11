#!/usr/bin/env python3
"""
Emergency Preparedness System Launcher
Safe startup with error handling and system status
"""

import sys
import os
from datetime import datetime

def main():
    print("🚨 EMERGENCY PREPAREDNESS SYSTEM")
    print("=" * 50)
    print(f"Starting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Initializing all 16 modules...")
    
    try:
        # Import and initialize system
        from integrated_preparedness_system import IntegratedPreparednessSystem
        
        print("✓ All modules imported successfully")
        
        # Create system instance
        system = IntegratedPreparednessSystem()
        
        print("✓ System initialized successfully")
        print(f"✓ Data directory: {system.data_dir}")
        print(f"✓ Active modules: {system.system_status['modules_active']}")
        
        print("\n🎯 System ready! Launching main interface...")
        print("=" * 50)
        
        # Run the system
        system.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 System shutdown requested by user")
        print("Stay safe and prepared!")
        
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if all required files are present")
        print("2. Ensure you have write permissions in this directory")
        print("3. Run 'python3 system_test.py' to diagnose issues")
        print(f"\nFor help, check the error details:")
        
        import traceback
        traceback.print_exc()
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)