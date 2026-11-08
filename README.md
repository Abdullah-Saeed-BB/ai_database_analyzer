# AI Database Analyzer
The AI Database Analyzer is an system generate SQL queries, execute them and feed it to the LLM model to analyze the results.

This branch is the API version which send request to LLMs host. If you want to use local LLM version, please go to the [Local branch](https://github.com/Abdullah-Saeed-BB/AI_database_analyzer).

## Tools
#### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

#### Frontend
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Lucide React](https://img.shields.io/badge/Lucide_React-FDE047?style=for-the-badge&logo=lucide&logoColor=black)
![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logo=recharts&logoColor=white)

## Project Structure

### Backend Structure
The backend is structured to cleanly separate database operations, AI utilities, and API routes.
```
backend/
├── db/                 # Database connection and setup operations
├── models/             # SQLAlchemy ORM models
├── schemas/            # Pydantic validation schemas
├── services/           # Core AI logic and query generators
│   ├── generator.py    # [MAIN FILE] Is the logic for that generates the SQL queries and analyze the results.
├── src/                # FastAPI application routes
│   ├── auth.py            # Authentication endpoints
│   ├── conversations.py   # AI query generation endpoints
│   ├── data.py            # Database tables exploration endpoints
│   └── users.py           # User management endpoints
├── main.py             # FastAPI entry point
└── requirements.txt    # Python dependencies
```

### Frontend Structure
```
frontend/
├── app/                # Next.js App Router (Pages, Layouts, and configurations)
├── components/         # Reusable React components (UI, Forms, Charts)
├── lib/                # Utility and API fetching functions
├── types/              # TypeScript interface definitions
└── package.json        # Node.js dependencies and scripts
```

## Installation

This project uses **PostgreSQL** database. Make sure you have PostgreSQL running on your host machine.

1. **Clone the project and checkout to the API version branch:**
   ```bash
   git clone https://github.com/Abdullah-Saeed-BB/AI_database_analyzer.git
   cd AI_database_analyzer
   git checkout API-version
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   pip install -r requirements.txt
   ```
   - Create a `.env` file in the **backend** folder, get the [OpenRouter](https://openrouter.ai/) API Key from their website for free, and update the username and passowrd to PostgreSQL user:

     ```.env
     DATABASE_URL="postgresql://[username]:[password]@localhost:5432/ai_db_analyzer"
     OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"

     JWT_SECRET_KEY="YOUR_JWT_SECRET_KEY"
     JWT_ALGORITHM="HS256"
     JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
     ```
   - Run the backend Application:

     ```bash
     uvicorn main:app --reload
     ```

3. **Frontend Setup:**
   - Create a `.env.local` in Frontend folder and paste the following:
  
      ```.env
      NEXT_PUBLIC_API_URL=http://localhost:8000

      JWT_SECRET_KEY="YOUR_JWT_SECRET_KEY"
      JWT_ALGORITHM="HS256"
      ```
   - Install the packages and run the application.
      ```bash
      cd frontend
      npm install
      npm run dev
      ```
> Note: If there issue happen after loging in, try delete `.next` and `node_modules` folders, then run `npm install` in the cmd.   

If you wanna use other models in OpenRouter, set the `MODEL_NAME` variable in `backend/.env` to the desired model:
```env
MODEL_NAME="YOUR_MODEL"
```

## Screenshots

