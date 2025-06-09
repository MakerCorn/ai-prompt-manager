#!/usr/bin/env python3
"""
Test LangWatch optimization integration
"""

import os
from langwatch_optimizer import langwatch_optimizer

def test_langwatch_optimization():
    """Test LangWatch optimization functionality"""
    
    print("🧪 Testing LangWatch Integration")
    print("=" * 50)
    
    # Test 1: Check status
    print("1. Checking LangWatch status...")
    status = langwatch_optimizer.get_status()
    print(f"   Available: {status['available']}")
    print(f"   Library installed: {status['library_installed']}")
    print(f"   Initialized: {status['initialized']}")
    print(f"   API key set: {status['api_key_set']}")
    
    # Test 2: Simple optimization
    print("\n2. Testing simple prompt optimization...")
    test_prompt = "Help me write an email"
    
    result = langwatch_optimizer.optimize_prompt(
        original_prompt=test_prompt,
        context="Business communication",
        target_model="gpt-4"
    )
    
    print(f"   Success: {result.success}")
    print(f"   Score: {result.optimization_score:.1f}")
    print(f"   Original: {result.original_prompt}")
    print(f"   Optimized: {result.optimized_prompt}")
    print(f"   Suggestions: {', '.join(result.suggestions)}")
    print(f"   Reasoning: {result.reasoning}")
    
    # Test 3: Complex optimization
    print("\n3. Testing complex prompt optimization...")
    complex_prompt = """
    Write a report about artificial intelligence. Include some background information, 
    current trends, and future implications. Make it informative.
    """
    
    result2 = langwatch_optimizer.optimize_prompt(
        original_prompt=complex_prompt.strip(),
        context="Technical writing for executives",
        target_model="gpt-4",
        optimization_goals=["clarity", "structure", "specificity", "executive-friendly"]
    )
    
    print(f"   Success: {result2.success}")
    print(f"   Score: {result2.optimization_score:.1f}")
    print(f"   Improvements: {len(result2.suggestions)} suggestions")
    print(f"   Length change: {len(result2.optimized_prompt)} vs {len(result2.original_prompt)} chars")
    
    # Test 4: Error handling
    print("\n4. Testing error handling...")
    empty_result = langwatch_optimizer.optimize_prompt(
        original_prompt="",
        context=None,
        target_model="gpt-4"
    )
    
    if not empty_result.success:
        print("   ✅ Empty prompt correctly handled")
    else:
        print("   ⚠️  Empty prompt not handled properly")
    
    print("\n" + "=" * 50)
    print("🎉 LangWatch integration test completed!")
    
    return result.success and result2.success

if __name__ == "__main__":
    success = test_langwatch_optimization()
    print(f"\nOverall result: {'✅ SUCCESS' if success else '❌ FAILED'}")