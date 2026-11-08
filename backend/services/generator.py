from sqlalchemy.orm import Session

from openai import OpenAI
import pandas as pd
import psycopg2 
import datetime
import time
import re
import os
from dotenv import load_dotenv
load_dotenv()

class Generator:
    def __init__(
        self,
        sql_instrc_file="./data/sql_generator_instruction.txt",
        text_instruction="./data/text_instruction.txt",
        text_model_temperature=0.13
    ):
        self.sql_instruction = open(sql_instrc_file).read()
        self.text_instruction = open(text_instruction).read()

        self.model = os.getenv("MODEL_NAME")
        self.text_model_temperature = text_model_temperature
        
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY,
        )

    def generate(self, prompt: str, conn: Session) -> str:
        errors = []

        sql_start_time = time.time()
        sql_query = self.generate_sql(prompt)

        i = 0
        while True:
            i += 1
            df = self.execute_sql(sql_query, conn)

            if isinstance(df, pd.DataFrame):
                break
            else:
                if i >= 3:
                    raise Exception(f"Error happen while executing the SQL query. Please try again.")
                sql_query = self.generate_sql(sql_query, error=df)
        sql_generation_time = time.time() - sql_start_time

        text_start_time = time.time()

        row_count = len(df)
        markdown = df.iloc[:10].to_markdown(index=False, tablefmt="github")
        data_note = (
            f"This data contains {row_count} rows" 
            if row_count > 0
            else f"No rows were returned by the query"
        ) 
        text_prompt = f"PROMPT: {prompt}\n\nDATA: ({data_note})\n{markdown}"

        response = self.generate_response(text_prompt)
        text_generation_time = time.time() - text_start_time

        metadata = self.generate_metadata(df)

        for obj_col in df.columns:
            try:
                if type(df.loc[0, obj_col]) in (datetime.date, datetime.datetime):
                    df[obj_col] = df[obj_col].apply(lambda dt: dt.isoformat())
                else:
                    date_datetime = pd.to_numeric(df[obj_col])
                    df[obj_col] = date_datetime.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except: pass
        data = df.to_dict(orient="list")

        return {
            "title": prompt,
            "prompt": prompt,
            "sql": sql_query,
            "text": response,
            "sql_generation_time": sql_generation_time,
            "text_generation_time": text_generation_time,
            "data_metadata": metadata,
            "data": data,
        }

    def generate_sql(self, prompt: str, error=None) -> str:
        if error:
            instrc = f"Fix this error: {error}\n\nSQL command:"
        else:
            instrc = self.sql_instruction

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "system", "content": instrc
            }, {
                "role": "user", "content": prompt
            }],
            temperature=0
        )
        text = response.choices[0].message.content
        sql_query = self.extract_sql_from_text(text)

        return sql_query

    def extract_sql_from_text(self, text: str) -> str:
        SQL_START_KEYWORDS = [
            "SELECT", "INSERT", "UPDATE", "DELETE",
            "WITH", "CREATE", "DROP", "ALTER"
        ]
        if not text:
            return ""

        text = re.sub(r"```sql", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        # text = text.replace("\\n", "\n")
        text = text.replace("\n", " ")

        text = text.strip()

        pattern = r"\b(" + "|".join(SQL_START_KEYWORDS) + r")\b"
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if not match:
            return ""

        start_index = match.start()
        sql_candidate = text[start_index:]

        semicolon_index = sql_candidate.find(";")
        if semicolon_index != -1:
            sql_candidate = sql_candidate[:semicolon_index + 1]

        # Stop at double newline (often explanation separator)
        split_double_newline = sql_candidate.split("\n\n")[0]

        sql_cleaned = re.sub(r"\s+", " ", split_double_newline).strip()

        return sql_cleaned

    def execute_sql(self, sql: str, conn: Session) -> pd.DataFrame:
        if sql.lower().strip().startswith("select"):
            for i in range(2):
                try:
                    df = pd.read_sql(sql, conn)
                    df.rename(inplace=True, columns=dict(map(
                        lambda col: (col, col.replace(".", "_")), df.columns
                    )))
                    return df
                except Exception as e:
                    err = e
                    sql = re.sub(r'(?<!%)%(?!%)', '%%', sql)
            raise err
        else:
            raise Exception("This SQL query doesn't execute SELECT statment query")

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "system", "content": self.text_instruction
                },{ 
                    "role": "user", "content": prompt
                }],
                temperature=self.text_model_temperature
            )
            text_res = response.choices[0].message.content

            return text_res
        except Exception as e:
            print("ERROR GENERATING TEXT RESPONSE:", e)
            return "Something went wrong while generating text response. Sorry :("

    def generate_metadata(self, df: pd.DataFrame) -> dict:
        metadata = {
            "columns": list(df.columns),
            "numerical": [],
            "categorical": [],
            "datetime": [],
            "stats": {},
        }

        def to_json_float(val):
            try:
                f_val = float(val)
                return f_val if pd.notna(f_val) else None
            except (ValueError, TypeError):
                return None

        try:
            for col in df.columns:
                series = df[col]

                if pd.api.types.is_datetime64_any_dtype(series):
                    metadata["datetime"].append(col)
                    metadata["stats"][col] = {
                        "type": "datetime",
                        "min": str(series.min()) if pd.notna(series.min()) else None,
                        "max": str(series.max()) if pd.notna(series.max()) else None,
                        "unique_values": int(series.nunique()),
                    }

                elif pd.api.types.is_numeric_dtype(series):
                    metadata["numerical"].append(col)
                    metadata["stats"][col] = {
                        "type": "numerical",
                        "min": to_json_float(series.min()),
                        "max": to_json_float(series.max()),
                        "mean": to_json_float(series.mean()),
                        "std": to_json_float(series.std()),
                    }

                else:
                    try:
                        parsed = pd.to_datetime(series)
                        metadata["datetime"].append(col)
                        metadata["stats"][col] = {
                            "type": "datetime",
                            "min": str(parsed.min()) if pd.notna(parsed.min()) else None,
                            "max": str(parsed.max()) if pd.notna(parsed.max()) else None,
                            "unique_values": int(parsed.nunique()),
                        }
                    except (ValueError, TypeError):
                        metadata["categorical"].append(col)
                        metadata["stats"][col] = {
                            "type": "categorical",
                            "unique_values": int(series.nunique()),
                        }
        except Exception as e:
            raise RuntimeError(f"Error while generating metadata, details: {e}")
            
        return metadata
