"""
MIT License

Copyright (c) 2025 MakerCorn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_PATH = os.getenv("DB_PATH", "prompts.db")
POSTGRES_DSN = os.getenv("POSTGRES_DSN")

class PromptDataManager:
    def __init__(self, db_path: str = None):
        self.db_type = DB_TYPE
        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                raise ImportError("psycopg2 is required for Postgres support. Please install it.")
            self.dsn = POSTGRES_DSN
            if not self.dsn:
                raise ValueError("POSTGRES_DSN environment variable must be set for Postgres.")
        else:
            self.db_path = db_path or DB_PATH
        self.init_database()

    def get_conn(self):
        if self.db_type == "postgres":
            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        else:
            return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT,
                    is_enhancement_prompt BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT,
                    is_enhancement_prompt BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            cursor.execute("PRAGMA table_info(prompts)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'is_enhancement_prompt' not in columns:
                cursor.execute('ALTER TABLE prompts ADD COLUMN is_enhancement_prompt BOOLEAN DEFAULT 0')
            if 'name' not in columns:
                cursor.execute('ALTER TABLE prompts ADD COLUMN name TEXT')
                cursor.execute('UPDATE prompts SET name = title WHERE name IS NULL')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS prompts_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        category TEXT DEFAULT 'Uncategorized',
                        tags TEXT,
                        is_enhancement_prompt BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('INSERT INTO prompts_new SELECT * FROM prompts')
                cursor.execute('DROP TABLE prompts')
                cursor.execute('ALTER TABLE prompts_new RENAME TO prompts')
        conn.commit()
        conn.close()

    def add_prompt(self, name: str, title: str, content: str, category: str, tags: str, is_enhancement_prompt: bool = False) -> str:
        if not name.strip():
            return "Error: Name is required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        name = name.strip()
        category = category.strip() or "Uncategorized"
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            cursor.execute('SELECT id FROM prompts WHERE name = %s', (name,))
        else:
            cursor.execute('SELECT id FROM prompts WHERE name = ?', (name,))
        if cursor.fetchone():
            conn.close()
            return f"Error: A prompt with name '{name}' already exists!"
        if self.db_type == "postgres":
            cursor.execute('''
                INSERT INTO prompts (name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (name, title.strip(), content.strip(), category, tags.strip(), is_enhancement_prompt,
                  datetime.now(), datetime.now()))
        else:
            cursor.execute('''
                INSERT INTO prompts (name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, title.strip(), content.strip(), category, tags.strip(), is_enhancement_prompt,
                  datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        prompt_type = "Enhancement prompt" if is_enhancement_prompt else "Prompt"
        return f"{prompt_type} '{name}' added successfully!"

    def update_prompt(self, original_name: str, new_name: str, title: str, content: str, category: str, tags: str, is_enhancement_prompt: bool = False) -> str:
        if not original_name.strip() or not new_name.strip():
            return "Error: Original name and new name are required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        original_name = original_name.strip()
        new_name = new_name.strip()
        category = category.strip() or "Uncategorized"
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM prompts WHERE name = ?', (original_name,))
        if not cursor.fetchone():
            conn.close()
            return f"Error: Prompt '{original_name}' not found!"
        if original_name != new_name:
            cursor.execute('SELECT id FROM prompts WHERE name = ?', (new_name,))
            if cursor.fetchone():
                conn.close()
                return f"Error: A prompt with name '{new_name}' already exists!"
        cursor.execute('''
            UPDATE prompts 
            SET name=?, title=?, content=?, category=?, tags=?, is_enhancement_prompt=?, updated_at=?
            WHERE name=?
        ''', (new_name, title.strip(), content.strip(), category, tags.strip(), is_enhancement_prompt,
              datetime.now().isoformat(), original_name))
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return "Prompt updated successfully!"
        else:
            conn.close()
            return "Error: Prompt not found!"

    def delete_prompt(self, name: str) -> str:
        if not name.strip():
            return "Error: Name is required!"
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prompts WHERE name = ?', (name.strip(),))
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"Prompt '{name}' deleted successfully!"
        else:
            conn.close()
            return f"Error: Prompt '{name}' not found!"

    def get_all_prompts(self, include_enhancement_prompts: bool = True) -> List[Dict]:
        conn = self.get_conn()
        cursor = conn.cursor()
        if include_enhancement_prompts:
            cursor.execute('''
                SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts ORDER BY category, name
            ''')
        else:
            cursor.execute('''
                SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts WHERE is_enhancement_prompt = 0 ORDER BY category, name
            ''')
        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                'id': row[0],
                'name': row[1],
                'title': row[2],
                'content': row[3],
                'category': row[4],
                'tags': row[5],
                'is_enhancement_prompt': bool(row[6]) if row[6] is not None else False,
                'created_at': row[7],
                'updated_at': row[8]
            })
        conn.close()
        return prompts

    def get_enhancement_prompts(self) -> List[Dict]:
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
            FROM prompts WHERE is_enhancement_prompt = 1 ORDER BY name
        ''')
        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                'id': row[0],
                'name': row[1],
                'title': row[2],
                'content': row[3],
                'category': row[4],
                'tags': row[5],
                'is_enhancement_prompt': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        conn.close()
        return prompts

    def get_categories(self) -> List[str]:
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM prompts ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def search_prompts(self, search_term: str, include_enhancement_prompts: bool = True) -> List[Dict]:
        if not search_term.strip():
            return self.get_all_prompts(include_enhancement_prompts)
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            like = f"%{search_term}%"
            if include_enhancement_prompts:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts 
                    WHERE name ILIKE %s OR title ILIKE %s OR content ILIKE %s OR tags ILIKE %s
                    ORDER BY category, name
                ''', (like, like, like, like))
            else:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts 
                    WHERE (name ILIKE %s OR title ILIKE %s OR content ILIKE %s OR tags ILIKE %s) AND is_enhancement_prompt = FALSE
                    ORDER BY category, name
                ''', (like, like, like, like))
        else:
            if include_enhancement_prompts:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts 
                    WHERE name LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ?
                    ORDER BY category, name
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts 
                    WHERE (name LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ?) AND is_enhancement_prompt = 0
                    ORDER BY category, name
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        prompts = []
        for row in cursor.fetchall():
            if self.db_type == "postgres":
                prompts.append({
                    'id': row['id'],
                    'name': row['name'],
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category'],
                    'tags': row['tags'],
                    'is_enhancement_prompt': bool(row['is_enhancement_prompt']) if row['is_enhancement_prompt'] is not None else False,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            else:
                prompts.append({
                    'id': row[0],
                    'name': row[1],
                    'title': row[2],
                    'content': row[3],
                    'category': row[4],
                    'tags': row[5],
                    'is_enhancement_prompt': bool(row[6]) if row[6] is not None else False,
                    'created_at': row[7],
                    'updated_at': row[8]
                })
        conn.close()
        return prompts

    def get_prompts_by_category(self, category: Optional[str] = None, include_enhancement_prompts: bool = True) -> List[Dict]:
        if not category or category == "All":
            return self.get_all_prompts(include_enhancement_prompts)
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            if include_enhancement_prompts:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE category = %s
                    ORDER BY name
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE category = %s AND is_enhancement_prompt = FALSE
                    ORDER BY name
                ''', (category,))
        else:
            if include_enhancement_prompts:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE category = ?
                    ORDER BY name
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE category = ? AND is_enhancement_prompt = 0
                    ORDER BY name
                ''', (category,))
        prompts = []
        for row in cursor.fetchall():
            if self.db_type == "postgres":
                prompts.append({
                    'id': row['id'],
                    'name': row['name'],
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category'],
                    'tags': row['tags'],
                    'is_enhancement_prompt': bool(row['is_enhancement_prompt']) if row['is_enhancement_prompt'] is not None else False,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            else:
                prompts.append({
                    'id': row[0],
                    'name': row[1],
                    'title': row[2],
                    'content': row[3],
                    'category': row[4],
                    'tags': row[5],
                    'is_enhancement_prompt': bool(row[6]) if row[6] is not None else False,
                    'created_at': row[7],
                    'updated_at': row[8]
                })
        conn.close()
        return prompts

    def get_prompt_by_name(self, name: str) -> Optional[Dict]:
        if not name.strip():
            return None
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            cursor.execute('''
                SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts WHERE name = %s
            ''', (name.strip(),))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category'],
                    'tags': row['tags'],
                    'is_enhancement_prompt': bool(row['is_enhancement_prompt']) if row['is_enhancement_prompt'] is not None else False,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        else:
            cursor.execute('''
                SELECT id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts WHERE name = ?
            ''', (name.strip(),))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'title': row[2],
                    'content': row[3],
                    'category': row[4],
                    'tags': row[5],
                    'is_enhancement_prompt': bool(row[6]) if row[6] is not None else False,
                    'created_at': row[7],
                    'updated_at': row[8]
                }
        return None
