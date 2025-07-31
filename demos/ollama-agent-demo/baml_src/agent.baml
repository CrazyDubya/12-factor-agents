// Import calculator tools from separate file

// Human interaction tools
class ClarificationRequest {
  intent "request_more_information"
  message string @description("Request clarification from the user")
}

class DoneForNow {
  intent "done_for_now"
  message string @description("Final response to the user")
}

// Model selection tools
class ListModels {
  intent "list_models"
  message string @description("Request to show available Ollama models")
}

class SelectModel {
  intent "select_model"
  model_name string @description("Name of the Ollama model to use")
}

// Group tool types
type CalculatorTools = AddTool | SubtractTool | MultiplyTool | DivideTool
type HumanTools = ClarificationRequest | DoneForNow
type ModelTools = ListModels | SelectModel
type AllTools = CalculatorTools | HumanTools | ModelTools

// Main agent function
function DetermineNextStep(
    thread: string,
    current_model: string
) -> AllTools {
    client OllamaLocal
    
    prompt #"
        {{ _.role("system") }}
        
        You are a helpful assistant that can help with math calculations and model management.
        
        Currently using model: {{ current_model }}
        
        Available tools:
        - Calculator operations (add, subtract, multiply, divide)
        - Request more information from user
        - List available Ollama models
        - Select a different Ollama model
        - Provide final response when done
        
        {{ _.role("user") }}
        
        Current conversation thread:
        {{ thread }}
        
        What should the next step be?
        
        Think step by step:
        1. Analyze what the user is asking for
        2. Determine if you need more information
        3. Choose the appropriate tool to use
        4. If it's a calculation, identify the numbers and operation
        5. If it's about models, help with listing or selection
        
        {{ ctx.output_format }}
    "#
}

// Basic tests
test BasicCalculation {
  functions [DetermineNextStep]
  args {
    thread #"<user_input>add 3 and 4</user_input>"#
    current_model "llama3.1:8b"
  }
}

test ModelListing {
  functions [DetermineNextStep]
  args {
    thread #"<user_input>list models</user_input>"#
    current_model "llama3.1:8b"
  }
}