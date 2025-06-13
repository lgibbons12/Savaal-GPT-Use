from playwright.sync_api import sync_playwright
import time
import os
from agent import GeminiComputer

# === CONFIG === #
PDF_DIR = "pdf_files"
OUTPUT_DIR = "gemini_responses"
PROMPT = "Generate 5 multiple-choice questions based on the content of the provided PDF and return only the questions and answer options in JSON format. Make sure it is in a code editor JSON format."
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

        computer = GeminiComputer(browser=browser, page=page)

    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        return

    for file in os.listdir(PDF_DIR):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join(PDF_DIR, file)

        try:
            print(f"Processing file: {file}")
            response = computer.process_file(file_path, PROMPT)

            # Save the response to a file    
            out_path = f"{OUTPUT_DIR}/{file[:-4]}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response)

            print(f"✅ Response for {file} saved to {out_path}")

            # ── NEW CHAT RESET ──
            computer.new_chat()

        except Exception as e:
            print(f"Error processing {file}: {e}")
            browser.close()
            playwright.stop()
            return
    browser.close()
    playwright.stop()
    print("✅ Finished processing all files.")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()