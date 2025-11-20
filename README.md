# FastAPI Project

A simple FastAPI application with a single API endpoint.

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration.

5. **Run the application:**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/hello?name=YourName` - Example API endpoint

