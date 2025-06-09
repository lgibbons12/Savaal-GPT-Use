from playwright.sync_api import sync_playwright
import base64
from typing import List, Dict
import time
import json
import os

os.makedirs("responses", exist_ok=True)

PROMPT = "Generate 5 multiple-choice questions based on the content of the provided PDF and return only the questions and answer options in JSON format."

class ChromeComputer:
    def __init__(self, browser=None, page=None):
        self.browser = browser
        self.page = page
        self.dimensions = (1024, 768)  # Default dimensions
    
    def get_dimensions(self):
        return self.dimensions
    
    def get_environment(self):
        return "browser"
    
    def get_current_url(self):
        return self.page.url
    
    def find(self, selectors, timeout = 1000):
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                element = self.page.wait_for_selector(selector, timeout=timeout)
                if element:
                    return element
            except:
                continue

        return None
    
    def screenshot(self):
        # Take screenshot and convert to base64
        screenshot = self.page.screenshot(type='png')
        return base64.b64encode(screenshot).decode('utf-8')
    
    def click(self, item, button='left'):
        # Click at specific coordinates
        item.click(button=button)
    
    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        self.page.mouse.move(x, y)
        self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
    
    def type(self, text, delay: float = 75):
        """
        Type `text` into the focused element, pausing `delay` ms between keystrokes.
        """
        self.page.keyboard.type(text, delay=delay)
    
    def press(self, key):
        # Press a key
        self.page.keyboard.press(key)
    
    def keypress(self, keys):
        """Handle multiple key presses"""
        # Map common key names to Playwright's format
        key_map = {
            'ENTER': 'Enter',
            'TAB': 'Tab',
            'ESCAPE': 'Escape',
            'BACKSPACE': 'Backspace',
            'DELETE': 'Delete',
            'ARROW_UP': 'ArrowUp',
            'ARROW_DOWN': 'ArrowDown',
            'ARROW_LEFT': 'ArrowLeft',
            'ARROW_RIGHT': 'ArrowRight',
            'HOME': 'Home',
            'END': 'End',
            'PAGE_UP': 'PageUp',
            'PAGE_DOWN': 'PageDown',
            'F1': 'F1',
            'F2': 'F2',
            'F3': 'F3',
            'F4': 'F4',
            'F5': 'F5',
            'F6': 'F6',
            'F7': 'F7',
            'F8': 'F8',
            'F9': 'F9',
            'F10': 'F10',
            'F11': 'F11',
            'F12': 'F12',
            'CTRL': 'Control',
            'SHIFT': 'Shift',
            'ALT': 'Alt',
            'META': 'Meta',
            'COMMAND': 'Meta',
            'WIN': 'Meta',
            'CMD': 'Meta',  # Map CMD to Meta for Windows
            'R': 'r'  # Add lowercase 'r' for refresh
        }
        
        for key in keys:
            # Convert key to uppercase for consistent mapping
            key_upper = key.upper()
            # Use mapped key if it exists, otherwise use the original key
            playwright_key = key_map.get(key_upper, key)
            self.page.keyboard.press(playwright_key)
    
    def wait(self, ms=1000):
        """Wait for specified milliseconds"""
        self.page.wait_for_timeout(ms)
    
    def navigate(self, url):
        """Navigate to a specific URL"""
        self.page.goto(url)
    
    def drag(self, path: List[Dict[str, int]]) -> None:
        if not path:
            return
        self.page.mouse.move(path[0]["x"], path[0]["y"])
        self.page.mouse.down()
        for point in path[1:]:
            self.page.mouse.move(point["x"], point["y"])
        self.page.mouse.up()
    
    def add_file(self, file_path: str) -> None:
        """Attach a file to the chat input"""
        file_input = self.page.query_selector("input[type='file']")
        if not file_input:
            raise RuntimeError("❌ Could not find the file-upload input")
        
        # Set the file input to the specified file
        file_input.set_input_files(file_path)
        print(f"✅ File '{file_path}' attached successfully")
    
    def save_to_file(self, filename="results.txt"):
        """Save the current page content to a file"""
        # Select all text with Ctrl+A
        self.page.keyboard.press("Control+a")
        # Copy the selected text
        self.page.keyboard.press("Control+c")
        # Get the clipboard content
        content = self.page.evaluate("""() => {
            return navigator.clipboard.readText();
        }""")
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Results saved to {filename}")




def main():
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    try:
        # Connect to existing Chrome instance
        page = browser.contexts[0].pages[0]  # Get the first page
        print("✅ Connected to existing Chrome session")

        computer = ChromeComputer(browser=browser, page=page)


        # try to find message area
        print("Looking for message input field...")
        
        # Try multiple selectors for the input field
        input_selectors = [
            "textarea[placeholder*='Message']",
            "textarea[data-id='root']",
            "#prompt-textarea",
            "textarea",
            "[contenteditable='true']"
        ]

        search_input = computer.find(input_selectors)

        if not search_input:
            raise ValueError("Could not find search input")
        
        computer.click(search_input)




        for file in os.listdir("pdf_files"):
            if not file.endswith(".pdf"):
                continue

            file_path = os.path.join("pdf_files", file)
            print(f"Attaching file: {file_path}")
            computer.add_file(file_path)

            # give the UI a moment to register the attachment
            time.sleep(2)

            search_input = computer.find(input_selectors)

            if not search_input:
                raise ValueError("Could not find search input")
            

            # 1) refocus the textarea
            computer.click(search_input)

            # 2) type your prompt
            computer.type(PROMPT)

            # wait a moment for the send button to appear/enabled
            # 1) Find all of the arrow‐icon SVGs (they all get class "icon-md")
            svgs = page.query_selector_all("svg.icon-md")

            if not svgs:
                raise RuntimeError("❌ Couldn't find any send‐icon SVGs on the page")

            # 2) Grab the last one (it belongs to the most recent composer)
            last_svg = svgs[-1]

            # 3) From that SVG, climb up to its enclosing <button>
            send_button = last_svg.evaluate_handle("el => el.closest('button')")

            # 4) Click it
            send_button.click()


            # 4) wait for the response
            time.sleep(20)
            print(f"✅ Response for {file} received")

            # 5) Find all code blocks in the response
            all_code_handles = page.locator("pre code").all()
            if not all_code_handles:
                raise RuntimeError("❌ No code blocks found in the response")
            
            response = all_code_handles[0].inner_text()
            print(f"✅ Response for {file} processed")
            # 6) Save the response to a file    
            out_path = f"responses/{file[:-4]}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"✅ Response for {file} saved to {out_path}")

            # ── NEW CHAT RESET ──
            # Navigate to the “new chat” page to start clean
            # 1) Locate the “New chat” link in the sidebar (it’s an <a>, not a button)
            new_chat_link = page.wait_for_selector("a:has-text('New chat')", timeout=5000)
            new_chat_link.click()
            time.sleep(10)

            

        print("✅ JSON response written to responses folder")


    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()