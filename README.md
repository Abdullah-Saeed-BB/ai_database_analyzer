# AI Database Analyzer
The AI Database Analyzer is an system generate SQL queries, execute them and feed it to the LLM model to analyze the results.

This branch is the local version which run the LLMs locally. If you want to use the LLM API version, please go to the [API-version](https://github.com/Abdullah-Saeed-BB/AI_database_analyzer/tree/API-version) branch.

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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Abdullah-Saeed-BB/AI_database_analyzer.git
   ```

2. **Prerequisites:** Ensure you have [Ollama](https://ollama.com/) locally installed and working. Make sure to download or verify the required models on your machine:
   ```bash
   ollama pull qwen2.5:1.5b
   ollama pull onekq/OneSQL-v0.1-Qwen:7B-Q4_K_M
   ```
   > **Warning:** The `onekq/OneSQL-v0.1-Qwen:7B-Q4_K_M` model size is 4.7GB and `qwen2.5:1.5b` model size is 986MB. Make sure you have enough storage space and RAM.

3. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   pip install -r requirements.txt
   ```
   - Create a `.env` file and paste the following, just update the username and password to PostgreSQL user in `DATABASE_URL`:
 
     ```.env
     DATABASE_URL="postgresql://[username]:[password]@localhost:5432/ai_db_analyzer"
     JWT_SECRET_KEY="YOUR_JWT_SECRET_KEY"
     JWT_ALGORITHM="HS256"
     JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
     ```
   - Run the backend Application:

     ```bash
     uvicorn main:app --reload
     ```

4. **Frontend Setup:**
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

If you wanna use other models from Ollama, just go to `backend/src/conversations.py` and apply the following to `generator = Generator()` code:
```python
generator = Generator(text_model="YOUR_TEXT_MODEL", sql_model="YOUR_SQL_MODEL")
```

## Screenshots

<img width="1920" height="1080" alt="AI answer countries orders" src="https://github.com/user-attachments/assets/2ffe6dda-8537-44ba-9ffc-bd22a6f1a5e6" />
<img width="1920" height="977" alt="AI answer correlation question about database" src="https://github.com/user-attachments/assets/2d8cf5cd-44a3-4a37-80c3-c9573aab89f8" />
<img width="1919" height="978" alt="AI get the last 3 orders" src="https://github.com/user-attachments/assets/25b9b6e4-255a-48cc-ba1b-4401d8980cf8" />
<img width="1920" height="1080" alt="View charts of countries orders" src="https://github.com/user-attachments/assets/664324dd-735c-499c-95a7-299767683311" />
<img width="1920" height="1080" alt="Ask AI analyzer page" src="https://github.com/user-attachments/assets/27c8f2d6-7d2d-4158-858a-56b4dc8a66f1" />

