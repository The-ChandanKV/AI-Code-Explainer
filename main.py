from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
from typing import List, Optional
import os

app = FastAPI(title="AI Code Explainer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model and tokenizer
MODEL_NAME = "facebook/bart-large-cnn"  # Changed to a more stable model
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading model and tokenizer...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            if torch.cuda.is_available():
                model = model.cuda()
            print("Model and tokenizer loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

class CodeRequest(BaseModel):
    code: str
    language: Optional[str] = None
    include_improvements: Optional[bool] = True

class CodeExplanation(BaseModel):
    line_number: int
    code: str
    explanation: str
    suggestions: Optional[List[str]] = None

class CodeAnalysis(BaseModel):
    complexity: str
    time_complexity: str
    space_complexity: str
    explanations: List[CodeExplanation]
    improvements: Optional[dict] = None

def analyze_complexity(code: str) -> dict:
    lines = code.split('\n')
    num_lines = len(lines)
    num_loops = len(re.findall(r'(for|while)', code))
    num_conditionals = len(re.findall(r'(if|else|elif|switch|case)', code))
    
    complexity = "Low"
    if num_loops > 2 or num_conditionals > 3:
        complexity = "High"
    elif num_loops > 0 or num_conditionals > 1:
        complexity = "Medium"
    
    return {
        "complexity": complexity,
        "time_complexity": "O(n)" if num_loops > 0 else "O(1)",
        "space_complexity": "O(n)" if "[]" in code or "{}" in code else "O(1)"
    }

def generate_explanation(code: str) -> List[CodeExplanation]:
    if not code.strip():
        return []
    
    lines = code.split('\n')
    explanations = []
    
    # Load model if not loaded
    if tokenizer is None or model is None:
        load_model()
    
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        # Generate a simple explanation based on code patterns
        explanation = generate_simple_explanation(line)
        
        # Generate suggestions for improvement
        suggestions = generate_suggestions(line)
        
        explanations.append(CodeExplanation(
            line_number=i,
            code=line,
            explanation=explanation,
            suggestions=suggestions if suggestions else None
        ))
    
    return explanations

def generate_simple_explanation(line: str) -> str:
    line = line.strip()
    
    if line.startswith('def ') or line.startswith('function '):
        return f"This defines a function named {line.split('(')[0].split()[-1]}"
    elif 'if ' in line:
        return "This is a conditional statement that checks a condition"
    elif 'for ' in line or 'while ' in line:
        return "This is a loop that iterates over a sequence or continues while a condition is true"
    elif 'return ' in line:
        return "This statement returns a value from the function"
    elif 'print(' in line:
        return "This statement outputs text to the console"
    elif '=' in line:
        return "This assigns a value to a variable"
    elif 'import ' in line:
        return "This imports a module or specific components from a module"
    elif 'class ' in line:
        return f"This defines a class named {line.split('(')[0].split()[-1]}"
    else:
        return "This line contains code that performs an operation"

def generate_suggestions(line: str) -> List[str]:
    suggestions = []
    
    if len(line) > 80:
        suggestions.append("Consider breaking this long line into multiple lines for better readability")
    
    if 'if ' in line and 'else' not in line:
        suggestions.append("Consider adding an else clause to handle the alternative case")
    
    if 'for ' in line and 'range(' in line:
        suggestions.append("Consider using list comprehension or built-in functions for better performance")
    
    if 'print(' in line:
        suggestions.append("Consider using proper logging instead of print statements")
    
    if 'try' in line and 'except' not in line:
        suggestions.append("Add proper exception handling")
    
    return suggestions

def generate_improvements(code: str) -> dict:
    improvements = {
        "time_complexity": None,
        "space_complexity": None,
        "best_practices": [],
        "error_fixes": []
    }
    
    # Analyze for potential improvements
    if "for" in code and "range" in code:
        improvements["time_complexity"] = "Consider using list comprehension or built-in functions for better performance"
    
    if "[]" in code or "{}" in code:
        improvements["space_complexity"] = "Consider using generators or iterators to reduce memory usage"
    
    # Add best practices
    if not any(line.strip().startswith("#") for line in code.split('\n')):
        improvements["best_practices"].append("Add comments to explain complex logic")
    
    if "print" in code:
        improvements["best_practices"].append("Consider using proper logging instead of print statements")
    
    # Add error fixes
    if "try" in code and "except" not in code:
        improvements["error_fixes"].append("Add proper exception handling")
    
    if "input()" in code:
        improvements["error_fixes"].append("Add input validation to prevent unexpected errors")
    
    return improvements

@app.post("/api/explain", response_model=CodeAnalysis)
async def explain_code(request: CodeRequest):
    try:
        # Generate explanations
        explanations = generate_explanation(request.code)
        
        # Analyze complexity
        complexity_analysis = analyze_complexity(request.code)
        
        # Generate improvements if requested
        improvements = generate_improvements(request.code) if request.include_improvements else None
        
        return CodeAnalysis(
            complexity=complexity_analysis["complexity"],
            time_complexity=complexity_analysis["time_complexity"],
            space_complexity=complexity_analysis["space_complexity"],
            explanations=explanations,
            improvements=improvements
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 