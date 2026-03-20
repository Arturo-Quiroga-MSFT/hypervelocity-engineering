#!/usr/bin/env python3
"""
Simple test script to verify the RAG dashboard components work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_demo_version():
    """Test the demo version functionality"""
    print("🧪 Testing RAG Dashboard Demo...")
    
    try:
        from rag_dashboard_demo import RAGDashboardDemo
        
        # Initialize the demo app
        app = RAGDashboardDemo()
        print("✅ Demo app initialized successfully")
        
        # Test mock document search
        config = {'top_k': 3, 'temperature': 0.1, 'simulation_delay': 0.1}
        results = app.search_documents("Azure AI Search", config)
        
        if results:
            print(f"✅ Search function works - found {len(results)} documents")
            print(f"   Top result: '{results[0].title}' (score: {results[0].score:.3f})")
        else:
            print("❌ Search function failed - no results")
            return False
        
        # Test answer generation
        context = "Azure AI Search is a cloud search service."
        answer = app.generate_answer("What is Azure AI Search?", context, config)
        
        if answer and len(answer) > 50:
            print("✅ Answer generation works")
            print(f"   Sample answer: {answer[:100]}...")
        else:
            print("❌ Answer generation failed")
            return False
        
        print("🎉 Demo version tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Demo version test failed: {e}")
        return False

def test_full_version():
    """Test the full version (without actually calling Azure services)"""
    print("🧪 Testing RAG Dashboard Full Version...")
    
    try:
        from rag_dashboard import RAGDashboard
        
        # Initialize the app
        app = RAGDashboard()
        print("✅ Full app initialized successfully")
        
        # Test configuration validation
        empty_config = {}
        if not app.validate_config(empty_config):
            print("✅ Configuration validation works correctly")
        else:
            print("❌ Configuration validation failed")
            return False
        
        print("✅ Full version basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Full version test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 RAG Dashboard Test Suite")
    print("=" * 50)
    
    demo_success = test_demo_version()
    print()
    full_success = test_full_version()
    
    print("\n" + "=" * 50)
    if demo_success and full_success:
        print("🎉 All tests passed! The RAG dashboard is ready to use.")
        print("\nTo run the demo: python launch.py --demo")
        print("To run the full version: python launch.py")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()