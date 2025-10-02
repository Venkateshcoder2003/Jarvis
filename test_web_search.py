#!/usr/bin/env python3
"""
Test web search functionality
"""

import asyncio
import sys
import os

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock RunContext for testing
class MockRunContext:
    pass

async def test_web_search():
    """Test the web search function"""
    
    print("🔍 Testing Web Search Functionality 🔍\n")
    
    try:
        from tools import search_web
        
        context = MockRunContext()
        
        test_queries = [
            "current weather",
            "latest news",
            "Python programming",
            "trending songs 2024"
        ]
        
        for query in test_queries:
            print(f"Testing query: '{query}'")
            print("-" * 50)
            
            try:
                result = await search_web(context, query)
                print(f"Result: {result[:200]}...")
                print("✅ Success!\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            await asyncio.sleep(1)  # Small delay between searches
            
        print("🔍 Web search testing completed!")
        
    except Exception as e:
        print(f"❌ Import or setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_web_search())