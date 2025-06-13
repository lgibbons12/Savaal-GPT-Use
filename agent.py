import time
class ChromeComputer:
    PROMPT = None
    OUTPUT_DIR = None

    
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

    def find_input(self):
        ...

    
    def process_file(self, pdf_path: str, prompt: str) -> str:
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
        
        search_input = self.find_input()

        if isinstance(self, GPTComputer):
            self.click(search_input)  # Refocus the textarea
            self.type(prompt)  # Type the prompt
        else:
            search_input.type(prompt, delay=50)
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

    OUTPUT_DIR = "responses"
    PROMPT = "Generate 5 multiple-choice questions based on the content of the provided PDF and return only the questions and answer options in JSON format."


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
    
    def find_input(self):
        INPUT_SELECTORS = [
            "textarea[placeholder*='Message']",
            "textarea[data-id='root']",
            "#prompt-textarea",
            "textarea",
            "[contenteditable='true']"
        ]
        search_input = self.find(INPUT_SELECTORS)
        if not search_input:
            raise ValueError("Could not find search input")
    
    def get_new_response(self) -> str:
        code_blocks = self.page.locator("pre code").all()
        if code_blocks:
            print("✅ Got response from code block")
            return code_blocks[0].inner_text()
        
        raise RuntimeError("❌ No response found in code blocks")
            



class GeminiComputer(ChromeComputer):
    """
    GeminiComputer is a specialized ChromeComputer for interacting with the Gemini chat interface.
    It includes methods for sending messages, attaching files, and retrieving responses.
    """

    OUTPUT_DIR = "gemini_responses"
    PROMPT = "Generate 5 multiple-choice questions based on the content of the provided PDF and return only the questions and answer options in JSON format. Make sure it is in a code editor JSON format."


    def __init__(self, browser=None, page=None):
        super().__init__(browser, page)

    def send(self):
        # Click the send icon directly
        send_icon = self.page.wait_for_selector("mat-icon.send-button-icon", timeout=5000)
        self.click(send_icon)
        print("✅ Clicked the send icon")
    
    def add_file(self, file_path: str) -> None:
        print(f"Adding file: {file_path}")
        # First click the + icon to open the Canvas menu
        add_btn = self.page.wait_for_selector("mat-icon[data-mat-icon-name='add_2']", timeout=5000)
        self.click(add_btn)
        print("✅ Clicked the + icon")
        
        time.sleep(1)  # Wait for menu to open
        
        # Then click "Upload files" and catch the filechooser event
        with self.page.expect_file_chooser() as fc_info:
            self.page.wait_for_selector("div.menu-text:has-text('Upload files')", timeout=5000).click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        print(f"✅ Uploaded file {file_path}")

    def find_input(self):
        textarea = (
            self.page.locator("textarea[placeholder='Ask Gemini']")
            .or_(self.page.locator("div[contenteditable='true'][role='textbox']"))
            .or_(self.page.locator("div[aria-label='Ask Gemini']"))
        )
        textarea.first.wait_for(timeout=5000)
        textarea.first.click()
        print("✅ Clicked the input area")
        return textarea.first  # Return the textarea element
    
    def new_chat(self):
        new_chat_label = self.page.wait_for_selector(
            "span[data-test-id='side-nav-action-button-content']:has-text('New chat')",
            timeout=5000
        )

        # 2) Climb up to the clickable list‐item container and click it
        new_chat_button = new_chat_label.evaluate_handle("el => el.closest('button, a')")
        self.click(new_chat_button)

        print("✅ New chat started")
    
    def get_new_response(self) -> str:
        try:
            json_text = self.page.evaluate(
                """() => {
                    // find all Monaco editors on the page
                    const editors = window.monaco.editor.getEditors
                    ? window.monaco.editor.getEditors()
                    : [window.monaco.editor.getEditor()];
                    if (!editors || !editors.length) {
                    throw new Error("No Monaco editor instance found");
                    }
                    // get the first one's model value
                    return editors[0].getModel().getValue();
                }"""
            )
            print("✅ Full JSON from Monaco model:")

            if not json_text:
                raise RuntimeError("No response from monaco editor")

            return json_text
        except Exception as e:
            print(f"Error getting response: {e}")
            print("Trying to get response from code blocks")
            code_blocks = self.page.locator("pre code").all()
            if code_blocks:
                print("✅ Got response from code block")
                return code_blocks[0].inner_text()
            
        raise RuntimeError("❌ No response found in either method")

    