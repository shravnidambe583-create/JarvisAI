import os
import sys
import subprocess
import webbrowser
import platform

# Selenium import
try:
    from selenium import webdriver as sel_driver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

from config import APP_PATHS

class AppController:
    """Manages application launches, terminations, web queries, and Selenium web automations."""
    
    def __init__(self):
        pass

    def open_app(self, app_name: str) -> bool:
        """Launch an application from configurations or path."""
        app_name = app_name.lower().strip()
        print(f"[AppControl] Launching app: {app_name}")
        
        # Check standard config mapping
        if app_name in APP_PATHS:
            path = APP_PATHS[app_name]
            
            # Resolve Windows username if needed
            if "{}" in path:
                username = os.getlogin()
                path = path.format(username)
                
            if os.path.exists(path) or platform.system() != "Windows":
                try:
                    subprocess.Popen(path, shell=True)
                    return True
                except Exception as e:
                    print(f"[AppControl] Launch error: {e}")
            else:
                # Look in alternate paths
                alt_key = f"{app_name}_alt"
                if alt_key in APP_PATHS:
                    alt_path = APP_PATHS[alt_key]
                    if os.path.exists(alt_path):
                        try:
                            subprocess.Popen(alt_path, shell=True)
                            return True
                        except Exception:
                            pass
        
        # If not explicitly in paths, attempt a general system start/launch
        try:
            if sys.platform == "win32":
                os.system(f"start {app_name}")
            else:
                os.system(f"xdg-open {app_name} >/dev/null 2>&1")
            return True
        except Exception:
            return False

    def close_app(self, app_name: str) -> bool:
        """Kills a running application process."""
        app_name = app_name.lower().strip()
        print(f"[AppControl] Closing app: {app_name}")
        
        # Map simple app names to process names
        proc_map = {
            "chrome": "chrome.exe",
            "vscode": "code.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "spotify": "spotify.exe"
        }
        
        proc_name = proc_map.get(app_name, f"{app_name}.exe" if sys.platform == "win32" else app_name)
        
        try:
            if sys.platform == "win32":
                subprocess.Popen(f"taskkill /f /im {proc_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                subprocess.Popen(f"pkill -f {proc_name}", shell=True)
            return True
        except Exception as e:
            print(f"[AppControl] Process kill error: {e}")
            return False

    def search_google(self, query: str) -> None:
        """Searches Google in the default browser."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)

    def search_youtube(self, query: str) -> None:
        """Searches YouTube in the default browser."""
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)

    def open_website(self, url: str) -> None:
        """Opens a website URL in the default browser."""
        if not url.startswith("http"):
            url = f"https://{url}"
        webbrowser.open(url)

    # --- Selenium Web Automation ---
    def run_selenium_search(self, query: str) -> str:
        """
        Uses Selenium to perform a search on Google and returns the text
        of the first result summary, as a demo of Selenium automation.
        """
        if not HAS_SELENIUM:
            return "Selenium is not installed. Defaulting to standard browser search."
            
        print(f"[AppControl] Running Selenium search for '{query}'...")
        driver = None
        try:
            # Configure options for headless browser to run cleanly in background
            options = sel_driver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            
            driver = sel_driver.Chrome(options=options)
            driver.get("https://www.google.com")
            
            # Find search box and search
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results and extract
            import time
            time.sleep(2) # Give it 2 seconds to load
            
            # Get headings or main summary
            results = driver.find_elements(By.XPATH, "//div[@class='g']")
            if results:
                summary = results[0].text
                return f"[Selenium Result Summary]:\n{summary}"
            return "No results found on Google."
        except Exception as e:
            return f"Selenium execution error: {e}"
        finally:
            if driver:
                driver.quit()
