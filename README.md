# ZaryahPlus Intern Task: Tool-Using Agent

## Overview
This is a custom-built, CLI-based AI agent for an Islamic utility assistant. It utilizes a raw `while` loop to plan, act, and observe using real tools without relying on heavyweight frameworks like LangChain.

## Tech Stack
* **Language:** Python
* **AI Model:** Google Gemini 3.5 Flash (via `google-generativeai` SDK)
* **APIs Used:** * Aladhan API (for Prayer Times and Hijri/Gregorian Date Conversion)
  * Al Quran Cloud API (for Quran Reference Lookups)

### Zakat Calculation Logic
The agent includes a local Zakat calculation tool that computes obligations without an external API. The logic is built as follows:
* **Inputs:** Accepts user cash savings, gold (in grams), and silver (in grams).
* **Valuation:** Uses approximate standard market rates (e.g., Gold at $80/g, Silver at $1/g) to calculate total asset worth. 
* **Nisab Threshold:** Compares the total asset worth against the standard gold Nisab (85 grams of gold).
* **Computation:** If the total assets meet or exceed the Nisab threshold, it applies the standard 2.5% (0.025) rate to determine the Zakat owed. If the assets are below the threshold, it accurately reports that no Zakat is due.

## Setup Instructions
1. Clone this repository.
2. Install the requirements: `pip install google-generativeai python-dotenv requests`
3. Create a `.env` file in the root directory and add your Gemini API key: `GEMINI_API_KEY="your_key_here"`
4. Run the agent: `python agent.py`

## Mandatory Questions

**1. How does your agent decide when to stop?**
The agent stops when it completes a loop iteration without calling any new tools. In the code, a `tool_was_called` flag is tracked while iterating through the model's response parts. If the model outputs standard text instead of a `function_call`, the flag remains false, the `while` loop breaks, and the final answer is printed to the user. There is also a hard limit of 5 iterations to prevent infinite loops.

**2. What happens when a tool fails?**
When a tool fails (e.g., an API goes down or the user provides an invalid city), the Python function catches the error in a `try/except` block and returns a string describing the failure (e.g., "Error: Could not retrieve prayer times"). This error string is fed back to the agent in the "Observe" step. The agent then reads this error, handles it gracefully, and explains the failure to the user in natural language instead of crashing.
