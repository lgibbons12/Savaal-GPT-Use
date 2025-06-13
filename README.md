# LLM UI Baseline Runner

**Automating LLM UI interactions for research baselines using Playwright.**


## 📝 Description

This project was developed to facilitate **running baselines for research projects by programmatically accessing the user interfaces (UIs) of various Large Language Models (LLMs)**. It leverages **Playwright** to interact with LLM UIs, allowing for automated collection of responses from different models based on input data. The primary goal is to standardize and streamline the process of gathering LLM outputs for comparative analysis in research.


## ✨ Features

* **UI-driven LLM Access:** Utilizes Playwright to programmatically access and interact with the user interfaces of various LLMs.
* **Modular Agent Architecture:** Features an `Agent.py` module with a base `ChromeComputer` class, from which specific LLM agent classes (e.g., `GPTComputer`, `GeminiComputer`) inherit, allowing for easy expansion to new models.
* **Automated Baseline Execution:** The `run_baseline.py` script automates the process of gathering LLM responses from a specified directory of PDF documents.
* **Structured Response Storage:** Automatically saves collected LLM responses into organized directories, such as `gemini_responses` and `gpt_responses`, for easy access and analysis.
* **Environment Setup Scripts:** Includes helper scripts (`start_chrome.ps1` for PowerShell/Windows and `start_chrome.sh` for Bash/Linux/macOS) to correctly configure the headless Chrome environment required by Playwright.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What software or tools do you need to have installed to run this project?

* [Python](https://www.python.org/) (e.g., v3.9.x or newer)
* [pip](https://pip.pypa.io/en/stable/) (Python package installer)
* [Git](https://git-scm.com/)
* **Playwright Browsers:** These will be installed via `playwright install`. Ensure you have the necessary system dependencies for Playwright to run browsers.

### Installation

A step-by-step guide on how to get your development environment set up.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-project-name.git](https://github.com/your-username/your-project-name.git)
    cd your-project-name
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install Playwright and other necessary Python packages.

3.  **Install Playwright browsers:**
    After installing the Python package, you need to install the browser binaries:
    ```bash
    playwright install
    ```


## 🏁 Usage

How to run and use your project after installation.

### Running the application

Before running the baseline script, you **must** start the Playwright-controlled Chrome instance using the provided scripts.

1.  **Start Chrome:**
    * **On Windows (using PowerShell):**
        ```powershell
        .\start_chrome.ps1
        ```
    * **On Linux/macOS (using Bash):**
        ```bash
        ./start_chrome.sh
        ```
    This script will open a Chrome browser instance that Playwright can control. Keep this window open while `run_baseline.py` is executing.

2.  **Run the baseline script:**
    Once Chrome is running, you can execute the main baseline script.
    ```bash
    python run_baseline.py /path/to/your/pdfs --llm gpt
    # or to gather Gemini responses
    python run_baseline.py /path/to/your/pdfs --llm gemini
    ```
    Replace `/path/to/your/pdfs` with the actual path to the directory containing your PDF documents. The `--llm` argument specifies which LLM agent to use.

### Basic Interactions

* **Preparing PDFs:** Place all PDF documents from which you want to gather LLM responses into a single directory.
* **Selecting LLM:** Use the `--llm` flag when running `run_baseline.py` to specify whether you want to interact with `gpt` (GPTComputer) or `gemini` (GeminiComputer).
* **Viewing Responses:** After `run_baseline.py` completes, check the newly created directories (e.g., `gpt_responses`, `gemini_responses`) in the project root for the collected LLM outputs. Each PDF's response will typically be saved as a separate file within these directories.

## ⚙️ Configuration

If your project requires specific configuration, explain how to do it here.

* **Agent Configuration:** Modify the `Agent.py` file to adjust how each LLM agent interacts with its respective UI (e.g., changing selectors, wait times).
* **Baseline Parameters:** The `run_baseline.py` script might expose additional command-line arguments for configuring aspects like output directory names, concurrency, or logging levels. Check the script's help (`python run_baseline.py --help`) for available options.

