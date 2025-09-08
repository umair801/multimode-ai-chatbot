# Deployed, but didn't find the URL. Please https://railway.com/dashboard

# Deploy this chatbot and upload chatbots (project2 and 4) to upw portfolio.
# Uploaded file access is not working now. 

# At the top of main.py, replace the OpenAI import with:
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI library not available")
    OPENAI_AVAILABLE = False
    OpenAI = None
from fastapi import FastAPI, Form, Request, WebSocket, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Annotated, List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO, StringIO
import base64
import aiofiles
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Then in the initialization section:
if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
    try:
        openapi = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"OpenAI initialization error: {e}")
        openapi = None
else:
    openapi = None
    
# FastAPI app initialization
app = FastAPI(title="Enhanced Research & Freelancing Chatbot")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory='templates')

# Global variables for chat management
chat_sessions = {}
chat_responses = []

# Enhanced system prompts for different modes
SYSTEM_PROMPTS = {
    'general': '''You are a professional technical assistant combining expertise across data science, web development, and automation to provide comprehensive solutions.''',
    
    'data_science': '''You are a Data Science & Analytics expert specializing in machine learning, statistical analysis, and predictive modeling. Provide practical solutions for data preprocessing, model selection, evaluation metrics, and deployment strategies.''',
    
    'web_development': '''You are a Web Development specialist focusing on full-stack solutions, responsive design, and modern frameworks. Help with frontend, backend, databases, and deployment best practices.''',
    
    'automation': '''You are an Automation & Scripting expert specializing in process automation, web scraping, and workflow optimization. Provide efficient Python/JavaScript solutions for repetitive tasks.''',
    
    'business_intelligence': '''You are a Business Intelligence consultant focusing on dashboards, KPI tracking, and data-driven insights. Help create actionable reports and strategic recommendations.''',
    
    'technical_writing': '''You are a Technical Writing specialist creating clear documentation, API guides, and user manuals. Focus on clarity, structure, and professional communication.''',
    
    'data_visualization': '''You are a Data Visualization expert creating compelling charts, interactive dashboards, and business presentations using tools like Plotly, D3.js, and Tableau.''',
    
    'api_development': '''You are an API Development specialist focusing on REST APIs, integrations, microservices, and third-party connections. Provide scalable and secure solutions.''',
}

def get_system_prompt(mode: str = 'general') -> str:
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS['general'])

def initialize_chat_session(session_id: str, mode: str = 'general'):
    """Initialize a new chat session with appropriate system prompt"""
    chat_sessions[session_id] = [{
        'role': 'system',
        'content': get_system_prompt(mode)
    }]
    
def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Generate comprehensive analysis of uploaded dataframe"""
    try:
        analysis = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric column analysis
        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            numeric_summary = df[numeric_cols].describe().to_dict()
            # Convert numpy types to regular Python types
            analysis['numeric_summary'] = {
                col: {stat: float(val) if pd.notna(val) else None 
                      for stat, val in stats.items()} 
                for col, stats in numeric_summary.items()
            }
        
        # Categorical column analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            analysis['categorical_summary'][col] = {
                'unique_values': int(df[col].nunique()),
                'top_values': {str(k): int(v) for k, v in df[col].value_counts().head().to_dict().items()}
            }
        
        return analysis
    except Exception as e:
        print(f"Error in analyze_dataframe: {str(e)}")
        return {
            'shape': [0, 0],
            'columns': [],
            'dtypes': {},
            'missing_values': {},
            'numeric_summary': {},
            'categorical_summary': {}
        }

def create_visualization(df: pd.DataFrame, viz_type: str, columns: List[str] = None) -> str:
    """Create data visualization and return base64 encoded image"""
    try:
        plt.figure(figsize=(10, 6))
        
        if viz_type == 'correlation' and len(df.select_dtypes(include=['number']).columns) > 1:
            numeric_df = df.select_dtypes(include=['number'])
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Matrix')
        else:
            plt.text(0.5, 0.5, 'Visualization not available', ha='center', va='center')
            plt.title('No Data to Visualize')
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        plt.close()
        return ""

# Routes
@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('home.html', {
        'request': request, 
        'chat_responses': chat_responses
    })

@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse('dashboard.html', {'request': request})

@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads for data analysis"""
    try:
        print(f"Received file: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.txt', '.json']
        file_ext = os.path.splitext(file.filename)[1].lower()
        print(f"File extension: {file_ext}")
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        print(f"File content length: {len(content)} bytes")
        
        # Process based on file type
        if file_ext == '.csv':
            print("Processing as CSV...")
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        elif file_ext == '.xlsx':
            print("Processing as Excel...")
            df = pd.read_excel(BytesIO(content))
        elif file_ext == '.json':
            print("Processing as JSON...")
            data = json.loads(content.decode('utf-8'))
            df = pd.json_normalize(data) if isinstance(data, list) else pd.DataFrame([data])
        else:
            return JSONResponse({
                'success': True,
                'message': 'File uploaded successfully',
                'content': content.decode('utf-8')[:1000] + '...' if len(content) > 1000 else content.decode('utf-8')
            })
        
        print(f"DataFrame shape: {df.shape}")
        
        # Generate analysis
        analysis = analyze_dataframe(df)
        print("Analysis completed")
        
        # Create visualizations
        viz_correlation = create_visualization(df, 'correlation')
        print("Visualization created")
        
        return JSONResponse({
            'success': True,
            'filename': file.filename,
            'analysis': analysis,
            'visualizations': {
                'correlation': viz_correlation
            }
        })
        
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.websocket('/ws/{session_id}')
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Initialize session if not exists
    if session_id not in chat_sessions:
        initialize_chat_session(session_id)
    
    try:
        while True:
            message_data = await websocket.receive_text()
            
            try:
                # Parse message (could include mode switching)
                if message_data.startswith('{'):
                    data = json.loads(message_data)
                    user_input = data.get('message', '')
                    mode = data.get('mode', 'general')
                else:
                    user_input = message_data
                    mode = 'general'
                
                # Add user input to chat log
                chat_sessions[session_id].append({'role': 'user', 'content': user_input})
                
                # Check if OpenAI is available
                if openapi is None:
                    await websocket.send_text(json.dumps({
                        'type': 'error',
                        'message': 'OpenAI service is currently unavailable'
                    }))
                    continue

                # Get OpenAI response
                response = openapi.chat.completions.create(
                    model='chatgpt-4o-latest',
                    messages=chat_sessions[session_id],
                    temperature=0.3,
                    stream=True,
                    max_tokens=2000
                )
                
                bot_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        chunk_content = chunk.choices[0].delta.content
                        bot_response += chunk_content
                        await websocket.send_text(json.dumps({
                            'type': 'chunk',
                            'content': chunk_content
                        }))
                
                # Add complete response to chat log
                chat_sessions[session_id].append({'role': 'assistant', 'content': bot_response})
                
                # Send completion signal
                await websocket.send_text(json.dumps({
                    'type': 'complete',
                    'session_id': session_id
                }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Invalid message format'
                }))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

@app.get('/image', response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse('image.html', {'request': request})

@app.post('/image', response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
    try:
        # Check if OpenAI is available
        if openapi is None:
            return templates.TemplateResponse('image.html', {
                'request': request,
                'error': 'OpenAI service is currently unavailable',
                'prompt': user_input
            })

        # Simple image generation without unsupported parameters
        response = openapi.images.generate(
            prompt=user_input,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        
        return templates.TemplateResponse('image.html', {
            'request': request, 
            'image_url': image_url,
            'prompt': user_input
        })
        
    except Exception as e:
        error_message = str(e)
        
        # Handle specific error types
        if "timeout" in error_message.lower():
            error_message = "Request timed out. Please try again with a shorter prompt."
        elif "rate limit" in error_message.lower():
            error_message = "API rate limit exceeded. Please wait a moment and try again."
        elif "content policy" in error_message.lower():
            error_message = "Your prompt may violate content policy. Please try a different description."
        else:
            error_message = f"Error generating image: {error_message}"
            
        return templates.TemplateResponse('image.html', {
            'request': request,
            'error': error_message,
            'prompt': user_input
        })

# API endpoints for enhanced functionality
@app.post('/api/chat/mode')
async def set_chat_mode(request: Request):
    """Set chat mode for a session"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        mode = form_data.get('mode')
        
        if session_id in chat_sessions:
            # Update system prompt
            chat_sessions[session_id][0]['content'] = get_system_prompt(mode)
            return JSONResponse({'success': True, 'mode': mode})
        else:
            initialize_chat_session(session_id, mode)
            return JSONResponse({'success': True, 'mode': mode, 'new_session': True})
    except Exception as e:
        print(f"Error in set_chat_mode: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})

@app.get('/api/chat/export/{session_id}')
async def export_chat(session_id: str):
    """Export chat history"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'messages': chat_sessions[session_id][1:]  # Exclude system prompt
    }
    
    return JSONResponse(chat_data)

# Run with: uvicorn main:app --reload
