// Calculator tool definitions - imported in agent.baml

class AddTool {
    intent "add" @description("Add two numbers together")
    a int | float @description("First number")
    b int | float @description("Second number")
}

class SubtractTool {
    intent "subtract" @description("Subtract second number from first")
    a int | float @description("First number (minuend)")
    b int | float @description("Second number (subtrahend)")
}

class MultiplyTool {
    intent "multiply" @description("Multiply two numbers")
    a int | float @description("First number")
    b int | float @description("Second number")
}

class DivideTool {
    intent "divide" @description("Divide first number by second")
    a int | float @description("Dividend")
    b int | float @description("Divisor")
}