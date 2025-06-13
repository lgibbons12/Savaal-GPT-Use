from playwright.sync_api import sync_playwright
from pathlib import Path
import typer
import os
from agent import GeminiComputer, GPTComputer

# === CONFIG === #
app = typer.Typer(help="Run a baseline for a given LLM and PDF directory")

SUPPORTED_LLMS = {"gemini", "gpt"}


@app.command()
def run(
    pdf_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        readable=True,
        dir_okay=True,
        resolve_path=True,
        help="Directory containing .pdf files to process",
    ),
    llm: str = typer.Option(
        ...,
        "--llm",
        "-l",
        case_sensitive=False,
        help="Large-language model to use: GPT or Gemini",
    ),
):
    llm = llm.strip().lower()

    if llm not in SUPPORTED_LLMS:
        typer.secho(f"❌ Unsupported LLM '{llm}'. Choose from {SUPPORTED_LLMS}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.echo(f"▶ Using LLM: {llm}")
    typer.echo(f"▶ Processing PDFs in: {pdf_dir}")
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

    try:
        # Connect to existing Chrome instance
        page = browser.contexts[0].pages[0]  # Get the first page
        typer.echo("✅ Connected to existing Chrome session")

        computer_cls = GPTComputer if llm == "gpt" else GeminiComputer
        computer = computer_cls(browser=browser, page=page)

    except Exception as e:
        typer.secho(f"❌ Error connecting to Chrome: {e}", fg=typer.colors.RED)
        return
    
    os.makedirs(computer.OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(pdf_dir):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_dir, file)

        try:
            typer.echo(f"▶ Processing file: {file}")
            response = computer.process_file(file_path)

            # Save the response to a file    
            out_path = f"{computer.OUTPUT_DIR}/{file[:-4]}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response)

            typer.echo(f"✅ Response for {file} saved to {out_path}")

            # ── NEW CHAT RESET ──
            computer.new_chat()

        except Exception as e:
            typer.secho(f"❌ Error processing {file}: {e}", fg=typer.colors.RED)
            browser.close()
            playwright.stop()
            return
        
    browser.close()
    playwright.stop()
    typer.echo("✅ Finished processing all files.")


if __name__ == "__main__":
    app()