#!/usr/bin/env python3
"""
Test script for the singing functionality
"""

import asyncio
import sys
import os
import logging

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the RunContext for testing
class MockRunContext:
    pass

async def test_singing():
    """Test the singing function with different requests"""
    
    print("🎤 Testing Alexa's Singing Capabilities! 🎤\n")
    
    # Import after path setup
    try:
        # Create a minimal version of the sing_song function for testing
        import random
        
        async def sing_song_test(context, song_request: str = "any song"):
            """Test version of sing_song function"""
            
            # Popular song themes and original lyrics snippets
            song_themes = {
                "happy": [
                    "🎵 Sunshine in my pocket, joy in every step,\nDancing through the morning, no regrets!\nLife is beautiful, oh can't you see,\nEvery moment's a melody! 🎵",
                    "🎵 Wake up with a smile, the world is bright,\nEverything's gonna be alright!\nSing it loud, sing it true,\nHappiness is me and you! 🎵"
                ],
                "love": [
                    "🎵 In your eyes I see the stars,\nIn your smile I find my peace,\nLove like ours will never fade,\nThis feeling will never cease! 🎵",
                    "🎵 Hold my hand through time and space,\nIn your heart I found my place,\nTogether we can face the storm,\nIn your love I'm safe and warm! 🎵"
                ],
                "inspirational": [
                    "🎵 Rise up high, reach for the sky,\nDreams are meant to make you fly!\nEvery step you take today,\nLeads you to a brighter way! 🎵",
                    "🎵 You are stronger than you know,\nLet your inner light just glow!\nEvery challenge makes you grow,\nThis is how the legends go! 🎵"
                ],
                "fun": [
                    "🎵 Dance like nobody's watching tonight,\nEverything's gonna be alright!\nMove your body, feel the beat,\nLife is good from head to feet! 🎵",
                    "🎵 Party time, let's celebrate,\nLife is good, don't hesitate!\nSing along and clap your hands,\nMusic brings us all as friends! 🎵"
                ]
            }
            
            # Trending/popular song types
            trending_songs = [
                "🎵 This is my moment, shining bright like gold,\nStory of my life is about to unfold!\nNothing's gonna stop me, I'm on my way,\nThis is my time, this is my day! 🎵",
                "🎵 We are the champions of our destiny,\nWriting our own song of victory!\nTogether we stand, together we shine,\nThe future is yours, the future is mine! 🎵",
                "🎵 Under neon lights we come alive,\nEvery heartbeat makes us feel so high!\nThis night is ours, let's make it count,\nEvery second, every sound! 🎵"
            ]
            
            song_request = song_request.lower().strip()
            
            # Check if it's a specific song request or general
            if any(word in song_request for word in ["any", "random", "trending", "popular"]):
                # Random trending song
                chosen_song = random.choice(trending_songs)
                song_type = "trending"
            elif "happy" in song_request or "cheerful" in song_request or "upbeat" in song_request:
                chosen_song = random.choice(song_themes["happy"])
                song_type = "happy"
            elif "love" in song_request or "romantic" in song_request:
                chosen_song = random.choice(song_themes["love"])
                song_type = "love"
            elif "inspire" in song_request or "motivat" in song_request or "uplift" in song_request:
                chosen_song = random.choice(song_themes["inspirational"])
                song_type = "inspirational"
            elif "fun" in song_request or "party" in song_request or "dance" in song_request:
                chosen_song = random.choice(song_themes["fun"])
                song_type = "fun"
            else:
                # For specific song requests, create an original inspired version
                chosen_song = f"🎵 Here's my version inspired by '{song_request}':\n{random.choice(trending_songs)}"
                song_type = "custom"
            
            # Song recommendations
            recommendations = [
                "🎶 'Blinding Lights' by The Weeknd",
                "🎶 'Good 4 U' by Olivia Rodrigo", 
                "🎶 'Levitating' by Dua Lipa",
                "🎶 'Stay' by The Kid LAROI & Justin Bieber",
                "🎶 'Heat Waves' by Glass Animals",
                "🎶 'Anti-Hero' by Taylor Swift",
                "🎶 'As It Was' by Harry Styles",
                "🎶 'Flowers' by Miley Cyrus",
                "🎶 'Unholy' by Sam Smith",
                "🎶 'Shivers' by Ed Sheeran"
            ]
            
            # Select 3 random recommendations
            selected_recommendations = random.sample(recommendations, 3)
            
            response = f"""Here's my song for you, buddy! 🎤

{chosen_song}

That was a fun {song_type} song! Hope you enjoyed it! 😊

Here are some trending songs you might want to check out:
{chr(10).join(selected_recommendations)}

Would you like me to sing another song for you? Just ask! 🎵"""
            
            return response
        
    except ImportError as e:
        print(f"Import error: {e}")
        return
    
    # Create a mock context
    context = MockRunContext()
    
    test_cases = [
        "any song",
        "happy song", 
        "love song",
        "sing Blinding Lights",
        "motivational song",
        "party song"
    ]
    
    for i, request in enumerate(test_cases, 1):
        print(f"🎵 Test {i}: '{request}'")
        print("-" * 50)
        
        try:
            result = await sing_song_test(context, request)
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")
        
        # Small delay between tests
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    print("Starting Alexa Singing Tests...")
    asyncio.run(test_singing())
    print("🎤 All tests completed! 🎤")