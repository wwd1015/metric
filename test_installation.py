#!/usr/bin/env python3
"""
Quick test script to verify Commercial Analytical Platform (CAP) installation and functionality.
Run this script to ensure everything is working correctly.
"""

import sys
import traceback

def test_imports():
    """Test all major imports."""
    print("🔍 Testing imports...")
    try:
        import cap
        print(f"  ✅ cap imported successfully (version: {cap.__version__})")
        
        from cap import register_metric, get_metric, list_metrics, call_metric
        print("  ✅ Core functions imported")
        
        from cap.api import create_api_app
        print("  ✅ API components imported")
        
        from cap.dashboard import create_dashboard_app
        print("  ✅ Dashboard components imported")
        
        from cap.core import get_registry
        print("  ✅ Registry components imported")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_registry():
    """Test metric registry functionality."""
    print("\n📊 Testing metric registry...")
    try:
        from cap.core import get_registry
        registry = get_registry()
        
        metrics = registry.list_all()
        print(f"  ✅ Registry loaded successfully")
        print(f"  📊 Found {len(metrics)} metrics:")
        
        for metric in metrics:
            print(f"    • {metric['id']}: {metric.get('name', 'No name')}")
        
        return len(metrics) > 0
    except Exception as e:
        print(f"  ❌ Registry test failed: {e}")
        traceback.print_exc()
        return False

def test_metric_calculation():
    """Test calling a metric."""
    print("\n🧪 Testing metric calculation...")
    try:
        from cap import call_metric, list_metrics
        
        metrics = list_metrics()
        if not metrics:
            print("  ⚠️  No metrics available to test")
            return False
        
        metric = metrics[0]
        metric_id = metric['id']
        print(f"  🧮 Testing metric: {metric_id}")

        kwargs = {}
        if metric_id == "demo_simple_calculator":
            import pandas as pd

            kwargs = {"input_data": pd.DataFrame({"value": [1, 2, 3]}), "operation": "sum"}

        result = call_metric(metric_id, **kwargs)
        
        print(f"  ✅ Metric calculation successful!")
        print(f"  📊 Result keys: {list(result.keys())}")
        
        # Check result types
        for key, value in result.items():
            print(f"    {key}: {type(value).__name__}")
        
        return True
    except Exception as e:
        print(f"  ❌ Metric calculation failed: {e}")
        traceback.print_exc()
        return False

def test_api_creation():
    """Test API app creation."""
    print("\n🌐 Testing API creation...")
    try:
        from cap.api import create_api_app
        app = create_api_app()
        print("  ✅ API app created successfully")
        return True
    except Exception as e:
        print(f"  ❌ API creation failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_creation():
    """Test dashboard app creation."""
    print("\n📊 Testing dashboard creation...")
    try:
        from cap.dashboard import create_dashboard_app
        app = create_dashboard_app()
        print("  ✅ Dashboard app created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Dashboard creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Commercial Analytical Platform (CAP) Installation Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Registry", test_registry), 
        ("Metric Calculation", test_metric_calculation),
        ("API Creation", test_api_creation),
        ("Dashboard Creation", test_dashboard_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Commercial Analytical Platform (CAP) is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Run: python -c \"from cap.scaffolding.cli import cli; cli()\" list")
        print("  2. Run: python -c \"from cap.scaffolding.cli import cli; cli()\" dashboard")
    print("  3. Try the Jupyter notebook: CAP_Demo.ipynb")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
