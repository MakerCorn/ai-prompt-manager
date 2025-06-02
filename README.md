# AI Prompt Manager Tool

To run the application:

Save the code as prompt_manager.py

Install dependencies:

    pip install gradio requests pandas

Run the application:

    python prompt_manager.py

Open your browser to http://localhost:7860

The application now includes all the features we discussed:

- [x] Name-based prompt management (required unique names)
- [x] Category organization with tree view
- [x] Prompt enhancement with different AI models
- [x] Multiple AI service support (OpenAI, LM Studio, Ollama, Llama.cpp)
- [x] Local SQLite database storage
- [x] Search and filtering capabilities
- [x] Proper sorting by category and name

## Database Configuration (.env)

The application supports both SQLite (default) and PostgreSQL for storing prompts and configuration. You can configure the database using a `.env` file in the project root.

### SQLite (default)
No configuration is needed. By default, the app uses a local `prompts.db` file.

**Optional:** To explicitly set the SQLite database file:

```
DB_TYPE=sqlite
DB_PATH=prompts.db
```

### PostgreSQL
To use PostgreSQL, you must have the `psycopg2` package installed. Set the following in your `.env` file:

```
DB_TYPE=postgres
POSTGRES_DSN=dbname=yourdb user=youruser password=yourpass host=localhost port=5432
```

- `DB_TYPE` must be `postgres` to enable PostgreSQL support.
- `POSTGRES_DSN` is the connection string for your PostgreSQL database.


### Example .env file
```
# For SQLite (default)
DB_TYPE=sqlite
DB_PATH=prompts.db

# For PostgreSQL
# DB_TYPE=postgres
# POSTGRES_DSN=dbname=yourdb user=youruser password=yourpass host=localhost port=5432
```

**Note:** The application will automatically detect and use the correct database based on your `.env` settings.