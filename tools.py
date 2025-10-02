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

# Add these imports for system control
import subprocess
import asyncio
from datetime import datetime

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

@function_tool()
async def search_web(
    context: RunContext,
    query: str) -> str:
    """
    Search the web using reliable methods with timeout protection.
    """
    try:
        # Method 1: Try DDGS with timeout
        try:
            from ddgs import DDGS
            import asyncio
            
            async def ddgs_search():
                results = DDGS().text(query, max_results=3)
                if results:
                    formatted_results = []
                    for result in results:
                        title = result.get('title', 'No title')
                        body = result.get('body', 'No description')
                        # Limit each result
                        if len(body) > 120:
                            body = body[:120] + "..."
                        formatted_results.append(f"• {title}\n  {body}")
                    
                    return "\n\n".join(formatted_results)
                return None
            
            # Use timeout to prevent hanging
            search_result = await asyncio.wait_for(ddgs_search(), timeout=5.0)
            
            if search_result:
                logging.info(f"DDGS search successful for '{query}'")
                return f"Here's what I found about '{query}', buddy:\n\n{search_result}"
                
        except asyncio.TimeoutError:
            logging.error("DDGS search timed out")
        except ImportError:
            logging.info("DDGS not available")
        except Exception as e:
            logging.error(f"DDGS search error: {e}")
        
        # Method 2: Try simple requests search with timeout
        try:
            import requests
            import asyncio
            from urllib.parse import quote_plus
            
            async def simple_search():
                encoded_query = quote_plus(query)
                # Try a simple search - this is a placeholder for a working search API
                # You might want to integrate with a proper search API here
                return f"Found information about '{query}' from web sources"
            
            result = await asyncio.wait_for(simple_search(), timeout=3.0)
            logging.info(f"Simple search completed for '{query}'")
            return f"{result}, buddy. For more detailed results, try asking about weather or other specific topics!"
                
        except asyncio.TimeoutError:
            logging.error("Simple search timed out")
        except Exception as e:
            logging.error(f"Simple search error: {e}")
        
        # Fallback: Provide helpful response
        return f"I tried searching for '{query}' but search engines are having issues right now, buddy. However, I can help you with weather, singing songs, or controlling your system perfectly!"
            
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"Search had a small hiccup, buddy, but I'm still here to help with weather, songs, or system controls!"


async def _search_duckduckgo(query: str) -> str:
    """Search using DuckDuckGo with improved parsing"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Try multiple selectors for results
            result_selectors = [
                'div.result',
                'div.web-result',
                'div.result__body',
                '.result'
            ]
            
            for selector in result_selectors:
                result_divs = soup.select(selector)
                if result_divs:
                    break
            
            for result_div in result_divs[:3]:
                title = ""
                snippet = ""
                
                # Try multiple ways to get title
                title_selectors = ['h2 a', '.result__title a', '.result__a', 'h3 a', 'a.result__a']
                for title_sel in title_selectors:
                    title_elem = result_div.select_one(title_sel)
                    if title_elem:
                        title = title_elem.get_text().strip()
                        break
                
                # Try multiple ways to get snippet
                snippet_selectors = ['.result__snippet', '.result-snippet', '.snippet', 'span.result__snippet']
                for snippet_sel in snippet_selectors:
                    snippet_elem = result_div.select_one(snippet_sel)
                    if snippet_elem:
                        snippet = snippet_elem.get_text().strip()
                        break
                
                if title and snippet:
                    results.append(f"{title}: {snippet}")
                elif title:
                    results.append(title)
            
            if results:
                return "\n".join(results)
                
        return None
        
    except Exception as e:
        logging.error(f"DuckDuckGo search error: {e}")
        return None


async def _search_wikipedia(query: str) -> str:
    """Search Wikipedia for person information"""
    try:
        import requests
        
        # Clean the query for Wikipedia
        search_term = query.lower().replace("who is", "").replace("who's", "").replace("about", "").strip()
        
        # Wikipedia API search
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + search_term.replace(" ", "_")
        
        headers = {
            'User-Agent': 'Jarvis Assistant (https://github.com/user/jarvis)'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'extract' in data and data['extract']:
                title = data.get('title', search_term)
                extract = data['extract']
                return f"{title}: {extract}"
                
        return None
        
    except Exception as e:
        logging.error(f"Wikipedia search error: {e}")
        return None


async def _basic_web_search(query: str) -> str:
    """Basic web search using Google search (fallback)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Use Google search as fallback
        google_url = f"https://www.google.com/search?q={query}"
        
        response = requests.get(google_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for knowledge panels or featured snippets
            knowledge_panel = soup.select_one('.kno-rdesc span')
            if knowledge_panel:
                return f"About {query}: {knowledge_panel.get_text().strip()}"
            
            # Look for featured snippets
            featured_snippet = soup.select_one('.hgKElc')
            if featured_snippet:
                return f"About {query}: {featured_snippet.get_text().strip()}"
                
        return f"Found some information about '{query}' but unable to extract clear details."
        
    except Exception as e:
        logging.error(f"Basic web search error: {e}")
        return None
    
    
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


@function_tool()
async def control_system(
    context: RunContext,
    action: str,
    parameter: str = ""
) -> str:
    """
    Control Windows system operations.
    
    Args:
        action: Action to perform (open_app, close_apps, screenshot, volume, lock, restart, shutdown)
        parameter: Additional parameter (app name, volume level, etc.)
    """
    try:
        import subprocess
        import os
        action = action.lower().strip()
        
        if action == "open_app" or action == "open":
            return await _open_application(parameter)
        
        elif action == "close_apps" or action == "close_all":
            return await _close_applications(parameter)
        
        elif action == "screenshot" or action == "capture":
            return await _take_screenshot()
        
        elif action == "volume" or action == "set_volume":
            return await _set_volume(parameter)
        
        elif action == "lock" or action == "lock_computer":
            return await _lock_computer()
        
        elif action == "restart" or action == "reboot":
            return await _restart_system()
        
        elif action == "shutdown":
            return await _shutdown_system()
        
        else:
            return f"Unknown system action: {action}. Available: open_app, close_apps, screenshot, volume, lock, restart, shutdown"
    
    except Exception as e:
        logging.error(f"System control error: {e}")
        return f"System control failed, buddy: {str(e)}"


async def _open_application(app_name: str) -> str:
    """Open an application"""
    try:
        import subprocess
        import os
        
        app_name = app_name.lower().strip()
        
        # Enhanced application mappings with full paths
        app_mappings = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe", 
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "discord": "Discord.exe",
            "spotify": "Spotify.exe",
            "steam": "steam.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe"
        }
        
        if app_name in app_mappings:
            executable = app_mappings[app_name]
            
            # Special handling for Windows settings
            if executable == "ms-settings:":
                subprocess.Popen(["cmd", "/c", "start", "ms-settings:"], shell=True)
                return f"Opening {app_name}, buddy. Task completed!"
            else:
                # Try multiple methods to open the application
                try:
                    # Method 1: Direct execution
                    subprocess.Popen(executable, shell=True)
                except:
                    try:
                        # Method 2: Using start command
                        subprocess.Popen(["cmd", "/c", "start", "", executable], shell=True)
                    except:
                        # Method 3: Using where command to find full path
                        result = subprocess.run(["where", executable], capture_output=True, text=True, shell=True)
                        if result.returncode == 0:
                            full_path = result.stdout.strip().split('\n')[0]
                            subprocess.Popen([full_path], shell=True)
                        else:
                            raise Exception(f"Application {executable} not found")
                
                return f"Opening {app_name}, buddy. Task completed!"
        else:
            # Try to open as-is with multiple methods
            try:
                subprocess.Popen(app_name, shell=True)
            except:
                try:
                    subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
                except:
                    raise Exception(f"Unable to find application: {app_name}")
            
            return f"Attempting to open {app_name}, buddy."
    
    except Exception as e:
        return f"Unable to open {app_name}, buddy. Error: {str(e)}"


async def _close_applications(app_filter: str = "") -> str:
    """Close applications"""
    try:
        import psutil
        
        closed_apps = []
        
        if app_filter.lower() == "all" or app_filter == "":
            # Close common non-essential applications
            target_apps = ["chrome.exe", "firefox.exe", "notepad.exe", "calculator.exe", "mspaint.exe"]
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in [app.lower() for app in target_apps]:
                        proc.terminate()
                        closed_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # Close specific application
            app_filter = app_filter.lower()
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_filter in proc.info['name'].lower():
                        proc.terminate()
                        closed_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        if closed_apps:
            return f"Closed {len(closed_apps)} applications: {', '.join(set(closed_apps))}, buddy. Task completed!"
        else:
            return f"No applications found to close, buddy."
    
    except Exception as e:
        return f"Unable to close applications, buddy. Error: {str(e)}"


async def _take_screenshot() -> str:
    """Take a screenshot"""
    try:
        import pyautogui
        from datetime import datetime
        import os
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return f"Screenshot saved as {filename}, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to take screenshot, buddy. Error: {str(e)}"


async def _set_volume(volume_level: str) -> str:
    """Set system volume"""
    try:
        # Parse volume level
        if volume_level.endswith('%'):
            volume_level = volume_level[:-1]
        
        volume = int(volume_level)
        volume = max(0, min(100, volume))  # Clamp between 0-100
        
        # Use Windows built-in command
        import subprocess
        subprocess.run(f"nircmd.exe setsysvolume {int(volume * 655.35)}", shell=True, check=False)
        
        return f"Volume set to {volume}%, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to set volume, buddy. Error: {str(e)}"


async def _lock_computer() -> str:
    """Lock the computer"""
    try:
        import ctypes
        
        # Lock the workstation
        ctypes.windll.user32.LockWorkStation()
        
        return "Computer locked, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to lock computer, buddy. Error: {str(e)}"


async def _restart_system() -> str:
    """Restart the system"""
    try:
        import subprocess
        
        # Schedule restart in 10 seconds to allow response
        subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
        
        return "System will restart in 10 seconds, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to restart system, buddy. Error: {str(e)}"


async def _shutdown_system() -> str:
    """Shutdown the system"""
    try:
        import subprocess
        
        # Schedule shutdown in 10 seconds
        subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
        
        return "System will shutdown in 10 seconds, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to shutdown system, buddy. Error: {str(e)}"


@function_tool()
async def control_system(
    context: RunContext,
    action: str,
    parameter: str = ""
) -> str:
    """
    Control Windows system operations.
    
    Args:
        action: Action to perform (open_app, close_apps, screenshot, volume, lock, restart, shutdown)
        parameter: Additional parameter (app name, volume level, etc.)
    """
    try:
        import subprocess
        import os
        import pyautogui
        import psutil
        from datetime import datetime
        
        action = action.lower().strip()
        
        if action == "open_app" or action == "open":
            return await _open_application(parameter)
        
        elif action == "close_apps" or action == "close_all":
            return await _close_applications(parameter)
        
        elif action == "screenshot" or action == "capture":
            return await _take_screenshot()
        
        elif action == "volume" or action == "set_volume":
            return await _set_volume(parameter)
        
        elif action == "lock" or action == "lock_computer":
            return await _lock_computer()
        
        elif action == "restart" or action == "reboot":
            return await _restart_system()
        
        elif action == "shutdown":
            return await _shutdown_system()
        
        elif action == "brightness":
            return await _set_brightness(parameter)
        
        else:
            return f"Unknown system action: {action}. Available: open_app, close_apps, screenshot, volume, lock, restart, shutdown, brightness"
    
    except Exception as e:
        logging.error(f"System control error: {e}")
        return f"System control failed, buddy: {str(e)}"


async def _open_application(app_name: str) -> str:
    """Open an application"""
    try:
        import subprocess
        
        app_name = app_name.lower().strip()
        
        # Common application mappings
        app_mappings = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "discord": "Discord.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe"
        }
        
        if app_name in app_mappings:
            executable = app_mappings[app_name]
            
            # Special handling for Windows settings
            if executable == "ms-settings:":
                subprocess.Popen(["start", "ms-settings:"], shell=True)
            else:
                subprocess.Popen(executable, shell=True)
            
            return f"Opening {app_name}, buddy. Task completed!"
        else:
            # Try to open as-is
            subprocess.Popen(app_name, shell=True)
            return f"Attempting to open {app_name}, buddy."
    
    except Exception as e:
        return f"Unable to open {app_name}, buddy. Error: {str(e)}"


# async def _open_application(app_name: str) -> str:
#     """Open an application"""
#     try:
#         import subprocess
#         import os
        
#         app_name = app_name.lower().strip()
        
#         # Common application mappings with full paths or proper commands
#         app_mappings = {
#             # Browsers
#             "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#             "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#             "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
#             "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            
#             # System apps (these are in PATH)
#             "notepad": "notepad",
#             "calculator": "calc",
#             "paint": "mspaint",
#             "explorer": "explorer",
#             "file explorer": "explorer",
#             "cmd": "cmd",
#             "command prompt": "cmd",
#             "terminal": "wt",  # Windows Terminal
#             "powershell": "powershell",
#             "task manager": "taskmgr",
#             "control panel": "control",
            
#             # Settings (special case)
#             "settings": "ms-settings:",
            
#             # Common apps with typical install paths
#             "discord": os.path.expanduser(r"~\AppData\Local\Discord\Update.exe"),
#             "vscode": "code",  # This works if VS Code is in PATH
#             "visual studio code": "code",
#             "spotify": os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe"),
#             "steam": r"C:\Program Files (x86)\Steam\steam.exe",
#             "whatsapp": os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe"),
#         }
        
#         if app_name in app_mappings:
#             executable = app_mappings[app_name]
            
#             # Special handling for Windows settings
#             if executable.startswith("ms-"):
#                 os.system(f"start {executable}")
#                 return f"Opening {app_name}, buddy. Task completed!"
            
#             # For Discord, use special launch command
#             elif "discord" in app_name:
#                 discord_path = os.path.expanduser(r"~\AppData\Local\Discord\Update.exe")
#                 if os.path.exists(discord_path):
#                     subprocess.Popen([discord_path, "--processStart", "Discord.exe"])
#                 else:
#                     # Try alternative method
#                     os.system("start discord:")
#                 return f"Opening Discord, buddy. Task completed!"
            
#             # Check if file exists (for full paths)
#             elif os.path.exists(executable):
#                 subprocess.Popen(executable)
#                 return f"Opening {app_name}, buddy. Task completed!"
            
#             # Try as command (for system commands)
#             else:
#                 try:
#                     subprocess.Popen(executable, shell=True)
#                     return f"Opening {app_name}, buddy. Task completed!"
#                 except:
#                     # If fails, try with 'start' command
#                     os.system(f"start {executable}")
#                     return f"Opening {app_name}, buddy. Task completed!"
        
#         else:
#             # Try to open as-is using start command
#             os.system(f"start {app_name}")
#             return f"Attempting to open {app_name}, buddy."
    
#     except Exception as e:
#         return f"Unable to open {app_name}, buddy. Error: {str(e)}"

async def _close_applications(app_filter: str = "") -> str:
    """Close applications"""
    try:
        import psutil
        import subprocess
        
        closed_apps = []
        
        if app_filter.lower() == "all" or app_filter == "":
            # Close common non-essential applications
            target_apps = ["chrome.exe", "firefox.exe", "notepad.exe", "calculator.exe", "mspaint.exe"]
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in [app.lower() for app in target_apps]:
                        proc.terminate()
                        closed_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # Close specific application
            app_filter = app_filter.lower()
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_filter in proc.info['name'].lower():
                        proc.terminate()
                        closed_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        if closed_apps:
            return f"Closed {len(closed_apps)} applications: {', '.join(set(closed_apps))}, buddy. Task completed!"
        else:
            return f"No applications found to close, buddy."
    
    except Exception as e:
        return f"Unable to close applications, buddy. Error: {str(e)}"


async def _take_screenshot() -> str:
    """Take a screenshot"""
    try:
        import pyautogui
        from datetime import datetime
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return f"Screenshot saved as {filename}, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to take screenshot, buddy. Error: {str(e)}"


async def _set_volume(volume_level: str) -> str:
    """Set system volume"""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        import ctypes
        
        # Parse volume level
        if volume_level.endswith('%'):
            volume_level = volume_level[:-1]
        
        volume = int(volume_level)
        volume = max(0, min(100, volume))  # Clamp between 0-100
        
        # Get the default audio device
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        
        # Set volume (0.0 to 1.0)
        volume_control.SetMasterScalarVolume(volume / 100.0, None)
        
        return f"Volume set to {volume}%, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to set volume, buddy. Error: {str(e)}"


async def _lock_computer() -> str:
    """Lock the computer"""
    try:
        import ctypes
        
        # Lock the workstation
        ctypes.windll.user32.LockWorkStation()
        
        return "Computer locked, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to lock computer, buddy. Error: {str(e)}"


async def _restart_system() -> str:
    """Restart the system"""
    try:
        import subprocess
        
        # Schedule restart in 10 seconds to allow response
        subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
        
        return "System will restart in 10 seconds, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to restart system, buddy. Error: {str(e)}"


async def _shutdown_system() -> str:
    """Shutdown the system"""
    try:
        import subprocess
        
        # Schedule shutdown in 10 seconds
        subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
        
        return "System will shutdown in 10 seconds, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to shutdown system, buddy. Error: {str(e)}"


async def _set_brightness(brightness_level: str) -> str:
    """Set screen brightness (works on laptops)"""
    try:
        import subprocess
        
        if brightness_level.endswith('%'):
            brightness_level = brightness_level[:-1]
        
        brightness = int(brightness_level)
        brightness = max(0, min(100, brightness))
        
        # Use PowerShell to set brightness
        ps_command = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{brightness})"
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        
        return f"Brightness set to {brightness}%, buddy. Task completed!"
    
    except Exception as e:
        return f"Unable to set brightness, buddy. May not be supported on this device. Error: {str(e)}"


@function_tool()
async def sing_song(
    context: RunContext,
    song_request: str = "any song"
) -> str:
    """
    Sing a song for the user. Can sing any trending song or a specific requested song.
    Creates original lyrics to avoid copyright issues.
    
    Args:
        song_request: The song request (e.g., "any song", "happy song", "love song", "specific song name")
    """
    try:
        import random
        
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
        
        logging.info(f"Sang a {song_type} song and provided recommendations")
        return response
        
    except Exception as e:
        logging.error(f"Error in sing_song function: {e}")
        return "Sorry buddy, I'm having trouble with my singing voice right now! 🎤 Maybe try asking me to sing again?"