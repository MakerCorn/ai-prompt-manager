#!/usr/bin/env python3
"""
Test Multi-Service Prompt Optimization Integration
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from langwatch_optimizer import PromptOptimizer, prompt_optimizer  # noqa: F401


def test_langwatch_optimization():
    """Test multi-service prompt optimization functionality"""

    print("🧪 Testing Multi-Service Prompt Optimization")
    print("=" * 50)

    # Test 1: Check status
    print("1. Checking optimizer status...")
    status = prompt_optimizer.get_status()
    print(f"   Service: {status['service']}")
    print(f"   Available: {status['available']}")
    print(f"   Initialized: {status['initialized']}")
    print(f"   API key set: {status['api_key_set']}")
    print(f"   Available services: {list(status['services_available'].keys())}")

    # Show which services are available
    available_services = [k for k, v in status["services_available"].items() if v]
    print(f"   Working services: {available_services}")

    # Test 2: Simple optimization
    print("\n2. Testing simple prompt optimization...")
    test_prompt = "Help me write an email"

    result = prompt_optimizer.optimize_prompt(
        original_prompt=test_prompt,
        context="Business communication",
        target_model="gpt-4",
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

    result2 = prompt_optimizer.optimize_prompt(
        original_prompt=complex_prompt.strip(),
        context="Technical writing for executives",
        target_model="gpt-4",
        optimization_goals=["clarity", "structure", "specificity", "effectiveness"],
    )

    print(f"   Success: {result2.success}")
    print(f"   Score: {result2.optimization_score:.1f}")
    print(f"   Improvements: {len(result2.suggestions)} suggestions")
    print(
        f"   Length change: {len(result2.optimized_prompt)} vs {len(result2.original_prompt)} chars"
    )

    # Test 4: Error handling
    print("\n4. Testing error handling...")
    empty_result = prompt_optimizer.optimize_prompt(
        original_prompt="", context=None, target_model="gpt-4"
    )

    if not empty_result.success:
        print("   ✅ Empty prompt correctly handled")
    else:
        print("   ⚠️  Empty prompt not handled properly")

    # Test 5: Service configuration test
    print("\n5. Testing service configuration...")

    # Test with different optimization goals
    test_goals = ["clarity", "effectiveness", "structure", "specificity", "creativity"]
    for goal in test_goals:
        result_goal = prompt_optimizer.optimize_prompt(
            original_prompt="Explain quantum computing",
            context="Educational content",
            target_model="gpt-4",
            optimization_goals=[goal],
        )
        if result_goal.success:
            print(
                f"   ✅ {goal.title()} optimization: Score {result_goal.optimization_score:.1f}"
            )
        else:
            print(f"   ❌ {goal.title()} optimization failed")

    print("\n" + "=" * 50)
    print("🎉 Multi-service prompt optimization test completed!")

    return result.success and result2.success


if __name__ == "__main__":
    success = test_langwatch_optimization()
    print(f"\nOverall result: {'✅ SUCCESS' if success else '❌ FAILED'}")
