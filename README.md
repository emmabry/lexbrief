# AI Policy Analyst: An NLP-Based Interface for Exploring, Summarising, and Questioning Policy Documents

# Running the app

Follow these steps to set up and run the web app locally.

## 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://git.cs.bham.ac.uk/projects-2024-25/erb465.git
cd erb465
```


## 2. Navigate to the backend

```bash
cd webapp
cd backend
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI backend:

```bash
python -m fastapi dev app.py  
```

## 3. Navigate to the frontend

```bash
cd ../../frontend
npm install
```

Run the frontend in development mode:

```bash
npm run dev
```

## 4. Navigate to the web page

The frontend runs on port 5173.