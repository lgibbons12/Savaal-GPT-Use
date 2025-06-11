import time
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
        ...
    
    def send(self):
        """Click the send button by svg lookup"""
        ...
    
    def get_new_response(self) -> str:
        ...


    
    def new_chat(self):
        """Click the 'New chat' button to start a new conversation"""
        ...

    
    def process_file(self, pdf_path: str, prompt: str, INPUT_SELECTORS: list = None) -> str:
        """        Process a PDF file by attaching it to the chat, sending a prompt, and retrieving the response.
        Args:
            pdf_path (str): Path to the PDF file to be processed.
            prompt (str): The prompt to send to the chat.
            INPUT_SELECTORS (list, optional): List of selectors to find the input field. Defaults to None.  
        Returns:
            str: The response from the chat after processing the PDF.
        """
        self.add_file(pdf_path)
        time.sleep(2)  # Wait for the file to be attached
        search_input = self.find(INPUT_SELECTORS)
        if not search_input:
            raise ValueError("Could not find search input")
        
        self.click(search_input)  # Refocus the textarea
        self.type(prompt)  # Type the prompt
        time.sleep(1)  # Wait for the send button to appear
        self.send()  # Click the send button
        time.sleep(20)  # Wait for the response

        response = self.get_new_response()

        return response


class GPTComputer(ChromeComputer):
    """
    GPTComputer is a specialized ChromeComputer for interacting with the GPT-4 chat interface.
    It includes methods for sending messages, attaching files, and retrieving responses.
    """

    def __init__(self, browser=None, page=None):
        super().__init__(browser, page)

    def send(self):
        # 1) Find all of the arrow‐icon SVGs (they all get class "icon-md")
        svgs = self.query_all("svg.icon-md")
        if not svgs:
            raise RuntimeError("❌ Couldn't find any send‐icon SVGs on the page")
        
        btn = svgs[-1].evaluate_handle("el => el.closest('button')")
        self.click(btn)
        print("✅ Send button clicked")
    
    def add_file(self, file_path: str) -> None:
        file_input = self.page.query_selector("input[type='file']")
        if not file_input:
            raise RuntimeError("❌ Could not find the file-upload input")
        
        # Set the file input to the specified file
        file_input.set_input_files(file_path)
        print(f"✅ File '{file_path}' attached successfully")
    
    def new_chat(self):
        new_chat = self.find("a:has-text('New chat')", timeout=5000)
        if not new_chat:
            raise RuntimeError("❌ Could not find 'New chat' link")
        
        self.click(new_chat)
        self.wait(500)
        print("✅ New chat started")
    
    def get_new_response(self) -> str:
        all_code_handles = self.page.locator("pre code").all()
        if not all_code_handles:
            raise RuntimeError("❌ No code blocks found in the response")
        
        return all_code_handles[0].inner_text()
    

class GeminiComputer(ChromeComputer):
    """
    GeminiComputer is a specialized ChromeComputer for interacting with the Gemini chat interface.
    It includes methods for sending messages, attaching files, and retrieving responses.
    """

    def __init__(self, browser=None, page=None):
        super().__init__(browser, page)

    def send(self):
        ...
    
    def add_file(self, file_path: str) -> None:
        ...
    
    def new_chat(self):
        ...
    
    def get_new_response(self) -> str:
        ...

    