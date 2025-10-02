# from dotenv import load_dotenv

# from livekit import agents
# from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
# from livekit.plugins import (
#     noise_cancellation,
#     openai
# )
# from livekit.plugins import google
# from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
# from tools import get_weather, search_web, send_email
# from mem0 import AsyncMemoryClient
# from mcp_client import MCPServerSse
# from mcp_client.agent_tools import MCPToolsIntegration
# import os
# import json
# import logging
# load_dotenv()


# class Assistant(Agent):
#     def __init__(self, chat_ctx=None) -> None:
#         super().__init__(
#             instructions=AGENT_INSTRUCTION,
#             llm=openai.realtime.RealtimeModel(
#                  voice="Aoede"
             
#             ),
#             tools=[
#                 get_weather,
#                 search_web,
#                 send_email
#             ],
#             chat_ctx=chat_ctx

#         )
        


# async def entrypoint(ctx: agents.JobContext):

#     async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
#         logging.info("Shutting down, saving chat context to memory...")

#         messages_formatted = [
#         ]

#         logging.info(f"Chat context messages: {chat_ctx.items}")

#         for item in chat_ctx.items:
#             content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)

#             if memory_str and memory_str in content_str:
#                 continue

#             if item.role in ['user', 'assistant']:
#                 messages_formatted.append({
#                     "role": item.role,
#                     "content": content_str.strip()
#                 })

#         logging.info(f"Formatted messages to add to memory: {messages_formatted}")
#         await mem0.add(messages_formatted, user_id="Venkatesh")
#         logging.info("Chat context saved to memory.")


#     session = AgentSession(
        
#     )
#     mem0 = AsyncMemoryClient()
#     user_name = 'Venkatesh'

#     results = await mem0.get_all(user_id=user_name)
#     initial_ctx = ChatContext()
#     memory_str = ''

#     if results:
#         memories = [
#             {
#                 "memory": result["memory"],
#                 "updated_at": result["updated_at"]
#             }
#             for result in results
#         ]
#         memory_str = json.dumps(memories)
#         logging.info(f"Memories: {memory_str}")
#         initial_ctx.add_message(
#             role="assistant",
#             content=f"The user's name is {user_name}, and this is relvant context about him: {memory_str}."
#         )

#     mcp_server = MCPServerSse(
#         params={"url": os.environ.get("N8N_MCP_SERVER_URL")},
#         cache_tools_list=True,
#         name="SSE MCP Server"
#     )

#     agent = await MCPToolsIntegration.create_agent_with_tools(
#         agent_class=Assistant, agent_kwargs={"chat_ctx": initial_ctx},
#         mcp_servers=[mcp_server]
#     )

#     await session.start(
#         room=ctx.room,
#         agent=agent,
#         room_input_options=RoomInputOptions(
#             # LiveKit Cloud enhanced noise cancellation
#             # - If self-hosting, omit this parameter
#             # - For telephony applications, use `BVCTelephony` for best results
#             video_enabled=True,
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     await ctx.connect()

#     await session.generate_reply(
#         instructions=SESSION_INSTRUCTION,
#     )

#     ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_str))

# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))



# data storing is happening but no knowlede base access 
# from dotenv import load_dotenv
# from livekit import agents
# from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
# from livekit.plugins import (
#     noise_cancellation,
# )
# from livekit.plugins import google
# from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
# from tools import get_weather, search_web, send_email
# from mem0 import AsyncMemoryClient
# import os
# import json
# import logging
# import asyncio
# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class Assistant(Agent):
#     def __init__(self, chat_ctx=None, mem0_client=None, user_name="Venkatesh") -> None:
#         super().__init__(
#             instructions=AGENT_INSTRUCTION,
#             llm=google.beta.realtime.RealtimeModel(
#                 voice="Aoede",
#                 temperature=0.8,
#             ),
#             tools=[
#                 get_weather,
#                 search_web,
#                 send_email
#             ],
#             chat_ctx=chat_ctx
#         )
#         self.mem0_client = mem0_client
#         self.user_name = user_name
#         self.message_count = 0
    
#     async def save_conversation_to_memory(self):
#         """Save conversation to mem0 database"""
#         if not self.mem0_client or not self.chat_ctx:
#             return
            
#         try:
#             messages_formatted = []
            
#             logger.info(f"Chat context has {len(self.chat_ctx.items)} items")
            
#             for item in self.chat_ctx.items:
#                 content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)
                
#                 # Skip system messages and memory context
#                 if item.role in ['user', 'assistant'] and not content_str.startswith("The user's name is"):
#                     messages_formatted.append({
#                         "role": item.role,
#                         "content": content_str.strip()
#                     })
            
#             if messages_formatted:
#                 logger.info(f"Saving {len(messages_formatted)} messages to memory")
#                 await self.mem0_client.add(messages_formatted, user_id=self.user_name)
#                 logger.info("Messages saved to mem0 database successfully")
#             else:
#                 logger.info("No new messages to save")
                
#         except Exception as e:
#             logger.error(f"Error saving to mem0: {e}")

# async def entrypoint(ctx: agents.JobContext):
    
#     # Initialize mem0 client
#     try:
#         mem0 = AsyncMemoryClient()
#         logger.info("Mem0 client initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize mem0 client: {e}")
#         mem0 = None

#     user_name = 'Venkatesh'
    
#     # Load existing memories
#     initial_ctx = ChatContext()
#     memory_str = ''
    
#     if mem0:
#         try:
#             results = await mem0.get_all(user_id=user_name)
            
#             if results:
#                 memories = [
#                     {
#                         "memory": result["memory"],
#                         "updated_at": result["updated_at"]
#                     }
#                     for result in results
#                 ]
#                 memory_str = json.dumps(memories, indent=2)
#                 logger.info(f"Loaded {len(memories)} memories from database")
                
#                 # Add memory context to initial chat
#                 initial_ctx.add_message(
#                     role="system",
#                     content=f"Previous conversation context for {user_name}: {memory_str}"
#                 )
#             else:
#                 logger.info("No previous memories found")
#         except Exception as e:
#             logger.error(f"Error loading memories: {e}")

#     # Create agent with mem0 integration
#     agent = Assistant(chat_ctx=initial_ctx, mem0_client=mem0, user_name=user_name)
    
#     session = AgentSession()

#     # Periodic memory save function
#     async def periodic_memory_save():
#         while True:
#             await asyncio.sleep(30)  # Save every 30 seconds
#             if hasattr(agent, 'save_conversation_to_memory'):
#                 await agent.save_conversation_to_memory()

#     # Shutdown hook for final save
#     async def shutdown_hook():
#         logger.info("Shutting down, performing final memory save...")
#         if hasattr(agent, 'save_conversation_to_memory'):
#             await agent.save_conversation_to_memory()
#         logger.info("Final memory save completed")

#     await session.start(
#         room=ctx.room,
#         agent=agent,
#         room_input_options=RoomInputOptions(
#             video_enabled=True,
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Start periodic memory saving
#     if mem0:
#         asyncio.create_task(periodic_memory_save())

#     await ctx.connect()

#     await session.generate_reply(
#         instructions=SESSION_INSTRUCTION,
#     )

#     # Add shutdown callback
#     ctx.add_shutdown_callback(shutdown_hook)

# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))


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
        # Create very simple instructions to reduce API load
        enhanced_instructions = """
You are Alexa, an AI assistant.

# Key Rules:
- Keep responses SHORT (1-2 sentences max)
- When user asks to sing, use sing_song tool IMMEDIATELY
- When user asks for search, use search_web tool
- When user asks weather, use get_weather tool
- Say "buddy" and be friendly but brief

# Tools:
- search_web: For web searches
- get_weather: For weather info  
- sing_song: For singing songs
- control_system: For PC control
- search_user_memory: For personal info
- send_email: For emails
"""
        
        super().__init__(
            instructions=enhanced_instructions,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.05,  # Extremely low for maximum stability
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
                search_user_memory, 
                control_system, # Use the function tool, not class method
                sing_song,
            ],
            chat_ctx=chat_ctx
        )
        self.mem0_client = mem0_client
        self.user_name = user_name
        self.message_count = 0
        self.last_save_count = 0
    
    async def save_conversation_to_memory(self):
        """Save conversation to mem0 database"""
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
                await self.mem0_client.add(messages_formatted[self.last_save_count:], user_id=self.user_name)
                self.last_save_count = len(messages_formatted)
                logger.info("New messages saved to mem0 database successfully")
            elif messages_formatted:
                logger.info(f"No new messages to save (total: {len(messages_formatted)}, last saved: {self.last_save_count})")
            else:
                logger.info("No messages to save")
                
        except Exception as e:
            logger.error(f"Error saving to mem0: {e}")

async def entrypoint(ctx: agents.JobContext):
    
    # Initialize mem0 client
    try:
        mem0 = AsyncMemoryClient()
        logger.info("Mem0 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize mem0 client: {e}")
        mem0 = None

    user_name = 'Venkatesh'
    
    # Load existing memories and create context
    initial_ctx = ChatContext()
    
    if mem0:
        try:
            # Get all memories to provide context
            results = await mem0.get_all(user_id=user_name)
            
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
        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    # Create agent with mem0 integration
    agent = Assistant(chat_ctx=initial_ctx, mem0_client=mem0, user_name=user_name)
    
    session = AgentSession()

    # Reduce memory save frequency to avoid overwhelming the API
    async def periodic_memory_save():
        while True:
            await asyncio.sleep(300)  # Increased to 5 minutes to reduce load
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
            await agent.save_conversation_to_memory()
        logger.info("Final memory save completed")

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Start periodic memory saving
    if mem0:
        asyncio.create_task(periodic_memory_save())
    
    # Simplified tool execution hook with less frequent checks
    async def tool_execution_hook():
        while True:
            await asyncio.sleep(60)  # Increased to 60 seconds to reduce overhead
            try:
                current_count = len(agent.chat_ctx.items) if agent.chat_ctx else 0
                if current_count > agent.message_count:
                    agent.message_count = current_count
                    logger.info("Tool execution detected, saving memory...")
                    await agent.save_conversation_to_memory()
            except Exception as e:
                logger.error(f"Tool execution hook error: {e}")
    
    if mem0:
        asyncio.create_task(tool_execution_hook())

    await ctx.connect()

    # Simplified session instructions with timeout handling
    try:
        # Use a shorter, more direct instruction to reduce timeout risk
        await asyncio.wait_for(
            session.generate_reply(instructions="You are Alexa. Use tools when requested."),
            timeout=10.0  # 10 second timeout
        )
    except asyncio.TimeoutError:
        logger.error("Generate reply timed out - continuing without initial reply")
    except Exception as e:
        logger.error(f"Generate reply error: {e} - continuing anyway")
    
    # Reduced immediate save
    logger.info("Initial conversation setup complete")
    try:
        if hasattr(agent, 'save_conversation_to_memory'):
            await agent.save_conversation_to_memory()
    except Exception as e:
        logger.error(f"Initial memory save failed: {e}")

    # Add shutdown callback
    ctx.add_shutdown_callback(shutdown_hook)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))