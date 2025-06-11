from playwright.sync_api import sync_playwright
import time
import os
from agent import GPTComputer

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









def main():
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    try:
        # Connect to existing Chrome instance
        page = browser.contexts[0].pages[0]  # Get the first page
        print("✅ Connected to existing Chrome session")

        computer = GPTComputer(browser=browser, page=page)

    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        return
    


    for file in os.listdir(PDF_DIR):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join("pdf_files", file)

        try:
            print(f"Processing file: {file}")
            response = computer.process_file(file_path, PROMPT, INPUT_SELECTORS)

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