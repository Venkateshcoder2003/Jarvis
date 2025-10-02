#!/usr/bin/env python3
"""
Test to verify the singing function is properly called
"""

import asyncio
import logging

# Mock the function tool decorator and RunContext for testing
def function_tool():
    def decorator(func):
        return func
    return decorator

class MockRunContext:
    pass

# Import the sing_song function directly
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_direct_sing_call():
    """Test calling the sing_song function directly"""
    print("🎤 Testing Direct Sing Function Call 🎤\n")
    
    try:
        # Import and test the actual function from tools
        from tools import sing_song
        
        context = MockRunContext()
        
        print("Testing: 'any song'")
        print("-" * 50)
        result = await sing_song(context, "any song")
        print(result)
        print("\n" + "="*60 + "\n")
        
        print("Testing: 'happy song'")
        print("-" * 50)
        result = await sing_song(context, "happy song")
        print(result)
        
        print("\n✅ Direct function calls work perfectly!")
        
    except Exception as e:
        print(f"❌ Error testing direct function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_sing_call())