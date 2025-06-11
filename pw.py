from playwright.sync_api import sync_playwright
import base64
from typing import List, Dict
import time
import json
import os

# === CONFIG === #
PDF_DIR = "pdf_files"
OUTPUT_DIR = "responses"
PROMPT = "Generate 5 multiple-choice questions based on the content of the provided PDF and return only the questions and answer options in JSON format."
INPUT_SELECTORS = [
    "textarea[placeholder*='Message']",
    "textarea[data-id='root']",
    "#prompt-textarea",
    "textarea",
    "[contenteditable='true']"
]

class ChromeComputer:
    
    def __init__(self, browser=None, page=None):
        self.browser = browser
        self.page = page


    
    def find(self, selectors, timeout = 3000):
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
    
    def query_all(self, selector: str):
        """Find a single element by selector"""
        return self.page.query_selector_all(selector)
    
    
    def click(self, handle, button='left'):
        # Click at specific coordinates
        handle.click(button=button)
    
    
    
    def type(self, text, delay: float = 75):
        """
        Type `text` into the focused element, pausing `delay` ms between keystrokes.
        """
        self.page.keyboard.type(text, delay=delay)
    
    
    def wait(self, ms: int):
        self.page.wait_for_timeout(ms)
    
    def add_file(self, file_path: str) -> None:
        """Attach a file to the chat input"""
        file_input = self.page.query_selector("input[type='file']")
        if not file_input:
            raise RuntimeError("❌ Could not find the file-upload input")
        
        # Set the file input to the specified file
        file_input.set_input_files(file_path)
        print(f"✅ File '{file_path}' attached successfully")
    
    def send(self):
        """Click the send button by svg lookup"""
        # 1) Find all of the arrow‐icon SVGs (they all get class "icon-md")
        svgs = self.query_all("svg.icon-md")
        if not svgs:
            raise RuntimeError("❌ Couldn't find any send‐icon SVGs on the page")
        
        btn = svgs[-1].evaluate_handle("el => el.closest('button')")
        self.click(btn)
        print("✅ Send button clicked")
    
    def get_new_response(self) -> str:
        all_code_handles = self.page.locator("pre code").all()
        if not all_code_handles:
            raise RuntimeError("❌ No code blocks found in the response")
        
        return all_code_handles[0].inner_text()


    
    def new_chat(self):
        """Click the 'New chat' button to start a new conversation"""
        new_chat = self.find("a:has-text('New chat')", timeout=5000)
        if not new_chat:
            raise RuntimeError("❌ Could not find 'New chat' link")
        
        self.click(new_chat)
        self.wait(500)
        print("✅ New chat started")




# === MAIN SCRIPT === #
def process_file(computer: ChromeComputer, pdf_path: str, prompt: str):
    computer.add_file(pdf_path)
    time.sleep(2)  # Wait for the file to be attached
    search_input = computer.find(INPUT_SELECTORS)
    if not search_input:
        raise ValueError("Could not find search input")
    
    computer.click(search_input)  # Refocus the textarea
    computer.type(prompt)  # Type the prompt
    time.sleep(1)  # Wait for the send button to appear
    computer.send()  # Click the send button
    time.sleep(20)  # Wait for the response

    response = computer.get_new_response()

    return response




def main():
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    try:
        # Connect to existing Chrome instance
        page = browser.contexts[0].pages[0]  # Get the first page
        print("✅ Connected to existing Chrome session")

        computer = ChromeComputer(browser=browser, page=page)

    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        return
    


    for file in os.listdir(PDF_DIR):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join("pdf_files", file)

        try:
            print(f"Processing file: {file}")
            response = process_file(computer, file_path, PROMPT)

            # 7) Save the response to a file    
            out_path = f"{OUTPUT_DIR}/{file[:-4]}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response)

            print(f"✅ Response for {file} saved to {out_path}")

            # ── NEW CHAT RESET ──
            # Navigate to the “new chat” page to start clean
            # 1) Locate the “New chat” link in the sidebar (it’s an <a>, not a button)
            computer.new_chat()


            print("✅ JSON response written to responses folder")

        except Exception as e:
            print(f"❌ Error processing {file}: {e}")
            continue

    # Close the browser
    browser.close()
    playwright.stop()
    print("✅ All files processed successfully. Browser closed.")
            

if __name__ == "__main__":
    os.makedirs("responses", exist_ok=True)
    main()