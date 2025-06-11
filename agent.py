
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