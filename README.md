# AI Code Explainer

A powerful, offline-first web application that provides natural language explanations for code snippets in multiple programming languages.

## Features

- 🎨 Sleek, developer-centric UI with dark theme
- 💻 Support for multiple programming languages (Python, JavaScript, Java, C++)
- 🔍 Line-by-line code explanations
- 🌙 Dark theme with VS Code-like interface
- 📝 Syntax highlighting for both code and explanations
- 🔄 Real-time explanation generation
- 💾 Offline operation with local ML models
- 📊 Code complexity analysis
- 📥 Export explanations as Markdown or PDF

## Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Monaco Editor
- TypeScript

### Backend
- FastAPI
- Transformers (HuggingFace)
- PyTorch
- ONNX Runtime

## Setup

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- pip
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-code-explainer.git
cd ai-code-explainer
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

4. Start the development servers:

Frontend:
```bash
cd frontend
npm run dev
```

Backend:
```bash
cd backend
uvicorn main:app --reload
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Paste your code or upload a file
3. Select the programming language (or use auto-detect)
4. Click "Explain" to get a detailed explanation
5. Use the export options to save your explanation



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
