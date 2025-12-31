"""Test script for the model factory."""

from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model, list_available_models, add_model

print("=" * 60)
print("Model Factory Test Suite")
print("=" * 60)

# Test 1: List available models
print("\n1. Testing list_available_models():")
models = list_available_models()
print(f"   Found {len(models)} models:")
for name, provider_model in sorted(models.items()):
    print(f"     - {name}: {provider_model}")

# Test 2: Test with OpenAI model (using friendly name)
print("\n2. Testing OpenAI model initialization (gpt-4o-mini):")
try:
    model = get_model("gpt-4o-mini")
    print(f"   [OK] Successfully created: {type(model).__name__}")
except Exception as e:
    print(f"   [FAIL] Failed: {str(e)}")

# Test 3: Test with Anthropic model (using friendly name)
print("\n3. Testing Anthropic model initialization (claude-sonnet):")
try:
    model = get_model("claude-sonnet", temperature=0.7)
    print(f"   [OK] Successfully created: {type(model).__name__}")
except Exception as e:
    print(f"   [FAIL] Failed: {str(e)}")

# Test 4: Test with convenience alias
print("\n4. Testing alias (smart -> claude-sonnet):")
try:
    model = get_model("smart")
    print(f"   [OK] Successfully created using alias: {type(model).__name__}")
except Exception as e:
    print(f"   [FAIL] Failed: {str(e)}")

# Test 5: Test error handling for invalid model
print("\n5. Testing error handling for invalid model:")
try:
    model = get_model("nonexistent-model")
    print(f"   [FAIL] Should have raised ValueError")
except ValueError as e:
    print(f"   [OK] Correctly raised ValueError")
    print(f"     Message: {str(e)[:80]}...")

# Test 6: Test add_model function
print("\n6. Testing dynamic model addition (add_model):")
try:
    add_model("test-model", "openai:test-model")
    models = list_available_models()
    if "test-model" in models:
        print(f"   [OK] Successfully added new model")
    else:
        print(f"   [FAIL] Model was not added")
except Exception as e:
    print(f"   [FAIL] Failed: {str(e)}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
