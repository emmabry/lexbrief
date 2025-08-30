# AI Policy Analyst: An NLP-Based Interface for Exploring, Summarising, and Questioning Policy Documents

# Running the app

Follow these steps to set up and run the web app locally.

## 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://git.cs.bham.ac.uk/projects-2024-25/erb465.git
cd erb465
```
## 2. Set up backend

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Navigate to the backend folder

```bash
cd webapp
cd backend
```

Run the FastAPI backend:

```bash
python -m fastapi dev app.py  
```

## 3. Set up frontend

Navigate to the frontend folder and install dependencies:

```bash
cd ../../frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

The frontend runs on port 5173. Access it by visiting:
http://localhost:5173/