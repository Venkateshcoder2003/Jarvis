# import logging
# from livekit.agents import function_tool, RunContext
# import requests
# from langchain_community.tools import DuckDuckGoSearchRun
# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart  
# from email.mime.text import MIMEText
# from typing import Optional

# @function_tool()
# async def get_weather(
#     context: RunContext,  # type: ignore
#     city: str) -> str:
#     """
#     Get the current weather for a given city.
#     """
#     try:
#         response = requests.get(
#             f"https://wttr.in/{city}?format=3")
#         if response.status_code == 200:
#             logging.info(f"Weather for {city}: {response.text.strip()}")
#             return response.text.strip()   
#         else:
#             logging.error(f"Failed to get weather for {city}: {response.status_code}")
#             return f"Could not retrieve weather for {city}."
#     except Exception as e:
#         logging.error(f"Error retrieving weather for {city}: {e}")
#         return f"An error occurred while retrieving weather for {city}." 

# @function_tool()
# async def search_web(
#     context: RunContext,  # type: ignore
#     query: str) -> str:
#     """
#     Search the web using DuckDuckGo.
#     """
#     try:
#         results = DuckDuckGoSearchRun().run(tool_input=query)
#         logging.info(f"Search results for '{query}': {results}")
#         return results
#     except Exception as e:
#         logging.error(f"Error searching the web for '{query}': {e}")
#         return f"An error occurred while searching the web for '{query}'."    

# @function_tool()    
# async def send_email(
#     context: RunContext,  # type: ignore
#     to_email: str,
#     subject: str,
#     message: str,
#     cc_email: Optional[str] = None
# ) -> str:
#     """
#     Send an email through Gmail.
    
#     Args:
#         to_email: Recipient email address
#         subject: Email subject line
#         message: Email body content
#         cc_email: Optional CC email address
#     """
#     try:
#         # Gmail SMTP configuration
#         smtp_server = "smtp.gmail.com"
#         smtp_port = 587
        
#         # Get credentials from environment variables
#         gmail_user = os.getenv("GMAIL_USER")
#         gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
#         if not gmail_user or not gmail_password:
#             logging.error("Gmail credentials not found in environment variables")
#             return "Email sending failed: Gmail credentials not configured."
        
#         # Create message
#         msg = MIMEMultipart()
#         msg['From'] = gmail_user
#         msg['To'] = to_email
#         msg['Subject'] = subject
        
#         # Add CC if provided
#         recipients = [to_email]
#         if cc_email:
#             msg['Cc'] = cc_email
#             recipients.append(cc_email)
        
#         # Attach message body
#         msg.attach(MIMEText(message, 'plain'))
        
#         # Connect to Gmail SMTP server
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()  # Enable TLS encryption
#         server.login(gmail_user, gmail_password)
        
#         # Send email
#         text = msg.as_string()
#         server.sendmail(gmail_user, recipients, text)
#         server.quit()
        
#         logging.info(f"Email sent successfully to {to_email}")
#         return f"Email sent successfully to {to_email}"
        
#     except smtplib.SMTPAuthenticationError:
#         logging.error("Gmail authentication failed")
#         return "Email sending failed: Authentication error. Please check your Gmail credentials."
#     except smtplib.SMTPException as e:
#         logging.error(f"SMTP error occurred: {e}")
#         return f"Email sending failed: SMTP error - {str(e)}"
#     except Exception as e:
#         logging.error(f"Error sending email: {e}")
#         return f"An error occurred while sending email: {str(e)}"


import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional

@function_tool()
async def search_user_memory(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the user's memory database for personal information and preferences.
    Use this when the user asks about their preferences, past conversations, or personal details.
    
    Args:
        query: What to search for (e.g., "favorite color", "preferences", "hobbies")
    """
    try:
        from mem0 import AsyncMemoryClient
        
        mem0 = AsyncMemoryClient()
        user_name = "Venkatesh"  # You can make this dynamic if needed
        
        results = await mem0.search(query=query, user_id=user_name)
        
        if results:
            memory_info = []
            for result in results:
                memory_info.append(result.get('memory', ''))
            
            found_memories = ". ".join(memory_info)
            logging.info(f"Found memories for query '{query}': {found_memories}")
            return f"I found this information about you: {found_memories}"
        else:
            logging.info(f"No memories found for query: {query}")
            return f"I don't have any stored information about {query}, buddy."
            
    except Exception as e:
        logging.error(f"Error searching user memory: {e}")
        return "I'm having trouble accessing my memory right now, buddy."
    

@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

# @function_tool()
# async def search_web(
#     context: RunContext,  # type: ignore
#     query: str) -> str:
#     """
#     Search the web using DuckDuckGo.
#     """
#     try:
#         results = DuckDuckGoSearchRun().run(tool_input=query)
#         logging.info(f"Search results for '{query}': {results}")
#         return results
#     except Exception as e:
#         logging.error(f"Error searching the web for '{query}': {e}")
#         return f"An error occurred while searching the web for '{query}'."    

@function_tool()
async def search_web(
    context: RunContext,
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use direct DuckDuckGo search
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse results (simplified)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result')[:3]:  # Top 3 results
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('div', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    results.append(f"{title}: {snippet}")
            
            if results:
                search_results = "\n".join(results)
                logging.info(f"Search results for '{query}': Found {len(results)} results")
                return search_results
            else:
                return f"No search results found for '{query}'"
        else:
            return f"Search service unavailable for '{query}'"
            
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"Unable to search the web right now, buddy. Error: {str(e)}"
    
    
@function_tool()    
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"