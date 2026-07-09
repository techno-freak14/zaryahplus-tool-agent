import os
import json
import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import tools

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key missing! Please ensure GEMINI_API_KEY is defined in your .env file.")

genai.configure(api_key=api_key)

TOOL_MAP = {
    "calculate_zakat": tools.calculate_zakat,
    "get_prayer_times": tools.get_prayer_times,
    "convert_date": tools.convert_date,
    "lookup_quran_verse": tools.lookup_quran_verse
}

available_tools = [
    tools.calculate_zakat,
    tools.get_prayer_times,
    tools.convert_date,
    tools.lookup_quran_verse
]

def run_agent_loop(user_prompt: str):
    # We will store the trace logs here to send to the UI
    trace_logs = []
    
    def log_trace(message):
        print(message)          # Still print to terminal
        trace_logs.append(message) # Save for the UI

    log_trace("\n" + "="*50)
    log_trace(f"--- STARTING NEW AGENT TRACE ---")
    log_trace(f"User Request: {user_prompt}")
    log_trace("="*50 + "\n")
    
    today_date = datetime.datetime.now().strftime("%d-%m-%Y")
    
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        tools=available_tools,
        system_instruction=(
            f"You are an expert Islamic utility assistant. "
            f"IMPORTANT CONTEXT: Today's real current date is {today_date}. "
            "You have access to specialized tools to answer calculations, dates, references, and prayer times. "
            "Always use the appropriate tool if the user's request requires objective data. Never make up data or religious texts. "
            "If a tool fails, report the error directly to the user. If no tool can handle the request, politely refuse to answer."
        )
    )
    
    chat = model.start_chat(enable_automatic_function_calling=False)
    response = chat.send_message(user_prompt)
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        tool_was_called = False
        function_responses = []
        
        if hasattr(response, 'parts') and response.parts:
            for part in response.parts:
                if part.function_call:
                    tool_was_called = True
                    name = part.function_call.name
                    args = {k: v for k, v in part.function_call.args.items()}
                    
                    log_trace(f"[TRACE - PLAN & ACT] Iteration {iteration}")
                    log_trace(f"  Agent decided to call tool: '{name}'")
                    log_trace(f"  Arguments provided: {json.dumps(args)}")
                    
                    if name in TOOL_MAP:
                        try:
                            observation = TOOL_MAP[name](**args)
                        except Exception as e:
                            observation = f"Error executing tool: {str(e)}"
                    else:
                        observation = f"Error: Tool '{name}' is not recognized."
                    
                    log_trace(f"[TRACE - OBSERVE]")
                    log_trace(f"  Tool Output: {observation}\n")
                    
                    func_resp = genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=name,
                            response={'result': observation}
                        )
                    )
                    function_responses.append(func_resp)
        
        if tool_was_called:
            response = chat.send_message(function_responses)
        else:
            # --- STOP CONDITION: RETURN TO UI ---
            final_answer = response.text
            log_trace("="*50)
            log_trace("[FINAL ANSWER FROM AGENT]")
            log_trace(final_answer)
            log_trace("="*50 + "\n")
            
            return {
                "answer": final_answer,
                "trace": "\n".join(trace_logs)
            }
            
    log_trace("[TRACE] Agent stopped automatically because it hit the maximum iteration safety ceiling.")
    return {"answer": "Error: Agent took too many steps.", "trace": "\n".join(trace_logs)}