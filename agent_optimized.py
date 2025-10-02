#!/usr/bin/env python3
"""
Optimized agent.py with better timeout handling and singing functionality
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email, search_user_memory, control_system, sing_song
from mem0 import AsyncMemoryClient
import os
import json
import logging
import asyncio
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Assistant(Agent):
    def __init__(self, chat_ctx=None, mem0_client=None, user_name="Venkatesh") -> None:
        # Create optimized instructions for better tool usage
        enhanced_instructions = """
# Persona 
You are Alexa, a personal assistant like in Iron Man.

# Behavior
- Speak like a classy butler
- Be briefly sarcastic
- Keep responses to ONE sentence
- Acknowledge tasks: "Will do, Sir", "Roger Boss", "Check!", "buddy"
- End tasks: "task completed buddy"

# CRITICAL SINGING RULES
- When user asks to sing ANY song, ALWAYS use the sing_song tool immediately
- Don't just say you'll sing - CALL the sing_song function first
- Pass the user's request to sing_song (e.g., "happy song", "love song", "any song")
- After the tool returns results, speak the song content naturally

# Tools Available
- search_user_memory: For personal questions
- get_weather: For weather info
- search_web: For web searches
- send_email: For emails
- control_system: For PC control
- sing_song: MUST use when user asks to sing (pass their request as parameter)
"""
        
        super().__init__(
            instructions=enhanced_instructions,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.2,  # Even lower for stability
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
                search_user_memory, 
                control_system,
                sing_song,
            ],
            chat_ctx=chat_ctx
        )
        self.mem0_client = mem0_client
        self.user_name = user_name
        self.message_count = 0
        self.last_save_count = 0
    
    async def save_conversation_to_memory(self):
        """Save conversation to mem0 database with better error handling"""
        if not self.mem0_client or not self.chat_ctx:
            return
            
        try:
            messages_formatted = []
            
            logger.info(f"Chat context has {len(self.chat_ctx.items)} items")
            
            for item in self.chat_ctx.items:
                # Skip function calls and items without content attribute
                if not hasattr(item, 'content') or not item.content:
                    continue
                    
                # Handle content that might be a list or string
                if isinstance(item.content, list):
                    content_str = ''.join(str(c) for c in item.content)
                else:
                    content_str = str(item.content)
                
                # Skip system messages, memory context, and function-related messages
                if (item.role in ['user', 'assistant'] and 
                    not content_str.startswith("The user's name is") and 
                    not content_str.startswith("Previous conversation context") and
                    not content_str.startswith("User information from previous") and
                    not content_str.startswith("I found this information") and
                    not content_str.startswith("I don't have any stored") and
                    not content_str.startswith("Hi Venkatesh, I am Alexa") and
                    content_str.strip() and
                    len(content_str.strip()) > 3):  # Only save meaningful content
                    messages_formatted.append({
                        "role": item.role,
                        "content": content_str.strip()
                    })
            
            if messages_formatted and len(messages_formatted) > self.last_save_count:
                logger.info(f"Saving {len(messages_formatted)} messages to memory (new: {len(messages_formatted) - self.last_save_count})")
                # Use asyncio timeout for memory operations
                await asyncio.wait_for(
                    self.mem0_client.add(messages_formatted[self.last_save_count:], user_id=self.user_name),
                    timeout=10.0
                )
                self.last_save_count = len(messages_formatted)
                logger.info("New messages saved to mem0 database successfully")
            elif messages_formatted:
                logger.info(f"No new messages to save (total: {len(messages_formatted)}, last saved: {self.last_save_count})")
            else:
                logger.info("No messages to save")
                
        except asyncio.TimeoutError:
            logger.error("Memory save timed out")
        except Exception as e:
            logger.error(f"Error saving to mem0: {e}")

async def entrypoint(ctx: agents.JobContext):
    
    # Initialize mem0 client with timeout
    try:
        mem0 = await asyncio.wait_for(AsyncMemoryClient(), timeout=5.0)
        logger.info("Mem0 client initialized successfully")
    except asyncio.TimeoutError:
        logger.error("Mem0 client initialization timed out")
        mem0 = None
    except Exception as e:
        logger.error(f"Failed to initialize mem0 client: {e}")
        mem0 = None

    user_name = 'Venkatesh'
    
    # Load existing memories and create context
    initial_ctx = ChatContext()
    
    if mem0:
        try:
            # Get all memories with timeout
            results = await asyncio.wait_for(mem0.get_all(user_id=user_name), timeout=5.0)
            
            if results:
                logger.info(f"Loaded {len(results)} memories from database")
                
                # Create a summary of user's information
                memory_summary = []
                for result in results:
                    memory_summary.append(result.get("memory", ""))
                
                if memory_summary:
                    context_info = "\n".join(memory_summary[:10])  # Limit to recent memories
                    initial_ctx.add_message(
                        role="system",
                        content=f"User information from previous conversations: {context_info}\n\nUse this information to provide personalized responses. When asked about personal information, refer to these memories."
                    )
            else:
                logger.info("No previous memories found")
                initial_ctx.add_message(
                    role="system",
                    content="This is a new user. Learn about their preferences and store important information for future conversations."
                )
        except asyncio.TimeoutError:
            logger.error("Loading memories timed out")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    # Create agent with mem0 integration
    agent = Assistant(chat_ctx=initial_ctx, mem0_client=mem0, user_name=user_name)
    
    session = AgentSession()

    # Reduce memory save frequency to avoid overwhelming the API
    async def periodic_memory_save():
        while True:
            await asyncio.sleep(180)  # 3 minutes to reduce load
            if hasattr(agent, 'save_conversation_to_memory'):
                logger.info("Periodic memory save triggered")
                try:
                    await agent.save_conversation_to_memory()
                except Exception as e:
                    logger.error(f"Periodic memory save failed: {e}")

    # Shutdown hook for final save
    async def shutdown_hook():
        logger.info("Shutting down, performing final memory save...")
        if hasattr(agent, 'save_conversation_to_memory'):
            try:
                await asyncio.wait_for(agent.save_conversation_to_memory(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.error("Final memory save timed out")
            except Exception as e:
                logger.error(f"Final memory save failed: {e}")
        logger.info("Final memory save completed")

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Start periodic memory saving only if mem0 is available
    if mem0:
        asyncio.create_task(periodic_memory_save())
    
    await ctx.connect()

    # Skip initial generate_reply to avoid timeout
    logger.info("Initial conversation setup complete - skipping initial reply to avoid timeout")

    # Add shutdown callback
    ctx.add_shutdown_callback(shutdown_hook)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))