import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Import the tools we built
import tools

# Load environment variables from our secret .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key missing! Please ensure GEMINI_API_KEY is defined in your .env file.")

# Configure the Gemini SDK
genai.configure(api_key=api_key)

# 1. Map string names to actual Python functions for execution mapping
TOOL_MAP = {
    "calculate_zakat": tools.calculate_zakat,
    "get_prayer_times": tools.get_prayer_times,
    "convert_date": tools.convert_date,
    "lookup_quran_verse": tools.lookup_quran_verse
}

# 2. Package all tools into the list format Gemini expects
available_tools = [
    tools.calculate_zakat,
    tools.get_prayer_times,
    tools.convert_date,
    tools.lookup_quran_verse
]

def run_agent_loop(user_prompt: str):
    print("\n" + "="*50)
    print(f"--- STARTING NEW AGENT TRACE ---")
    print(f"User Request: {user_prompt}")
    print("="*50 + "\n")
    
    # Initialize a chat session using gemini-3.5-flash with our tools declared
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        tools=available_tools,
        system_instruction=(
            "You are an expert Islamic utility assistant. You have access to specialized tools "
            "to answer calculations, dates, references, and prayer times. Always use the appropriate "
            "tool if the user's request requires objective data. Never make up data or religious texts. "
            "If a tool fails, report the error directly to the user. If no tool can handle the request, "
            "politely refuse to answer."
        )
    )
    
    # Start chat to maintain history across loops automatically
    chat = model.start_chat(enable_automatic_function_calling=False)
    
    # Send initial user question
    response = chat.send_message(user_prompt)
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Flag to track if the model decided to act during this loop
        tool_was_called = False
        
        # Check through the response parts to see if the model wants to call a tool
        if hasattr(response, 'parts'):
            for part in response.parts:
                if part.function_call:
                    tool_was_called = True
                    name = part.function_call.name
                    
                    # Safely convert the protobuf arguments into a standard Python dictionary
                    args = {k: v for k, v in part.function_call.args.items()}
                    
                    # --- TRACE STEP ---
                    print(f"[TRACE - PLAN & ACT] Iteration {iteration}")
                    print(f"  Agent decided to call tool: '{name}'")
                    print(f"  Arguments provided by agent: {json.dumps(args)}")
                    
                    # Execute the real tool dynamically
                    if name in TOOL_MAP:
                        try:
                            observation = TOOL_MAP[name](**args)
                        except Exception as e:
                            observation = f"Error executing tool: {str(e)}"
                    else:
                        observation = f"Error: Tool '{name}' is not recognized."
                    
                    # --- TRACE STEP ---
                    print(f"[TRACE - OBSERVE]")
                    print(f"  Tool Output: {observation}\n")
                    
                    # Feed the observation back to the model as a function response 
                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=name,
                                response={'result': observation}
                            )
                        )
                    )
                    
                    # Break out of the parts loop to allow the main while loop to process the new response
                    break 
        
        # --- STOP CONDITION ---
        # If we looped through all parts and no tool was called, we are done!
        if not tool_was_called:
            print("="*50)
            print("[FINAL ANSWER FROM AGENT]")
            print(response.text)
            print("="*50 + "\n")
            return
            
    print("[TRACE] Agent stopped automatically because it hit the maximum iteration safety ceiling.")

# Quick inline testing block to try out the system
if __name__ == "__main__":
    # Test a query requiring tool chaining (Prayer times + Date conversion)
    sample_query = "What are the prayer times for London today, and what is today's date converted to a Hijri date?"
    run_agent_loop(sample_query)