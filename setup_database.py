import database as db
from pathlib import Path

def setup_database():
    print("=" * 50)
    print("QuizMaster - Database Setup")
    print("=" * 50)

    print("\nDatabase tables created!")

    print("\nCreating admin user...")
    success, message = db.create_user("admin", "admin123", is_admin=True)
    print(f"  {message}")

    print("\nCreating student user...")
    success, message = db.create_user("student", "student123", is_admin=False)
    print(f"  {message}")

    print("\nMigrating questions from JSON...")
    json_path = Path("data/questions.json")
    if json_path.exists():
        count = db.migrate_json_to_db(json_path)
        print(f"  Migrated {count} questions!")
    else:
        print(f"  JSON not found at {json_path} - add questions via Admin Panel")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("Run: streamlit run Home.py")
    print("=" * 50)

if __name__ == "__main__":
    setup_database()
```

---

**8. requirements.txt**
```
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.28.0
pypdf>=3.0.0
python-pptx>=0.6.21
python-docx>=1.1.0