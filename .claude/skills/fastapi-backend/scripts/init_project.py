#!/usr/bin/env python3
"""
Initialize a new FastAPI project with uv
"""

import os
import shutil
import sys
from pathlib import Path


def init_project(project_name: str, target_dir: str = "."):
    """Initialize a new FastAPI project"""
    
    # Get the skill directory (parent of scripts/)
    skill_dir = Path(__file__).parent.parent
    boilerplate_dir = skill_dir / "assets" / "boilerplate"
    
    # Create project directory
    project_path = Path(target_dir) / project_name
    project_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Initializing FastAPI project: {project_name}")
    print(f"   Location: {project_path.absolute()}")
    
    # Copy boilerplate files
    files_to_copy = [
        "main.py",
        "pyproject.toml",
        ".env.example",
        "constants.py"
    ]
    
    for file_name in files_to_copy:
        src = boilerplate_dir / file_name
        dst = project_path / file_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Created {file_name}")
        else:
            print(f"⚠️  Warning: {file_name} not found in boilerplate")
    
    # Create additional directories
    (project_path / "tests").mkdir(exist_ok=True)
    print("✅ Created tests/")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# uv
.uv/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
"""
    (project_path / ".gitignore").write_text(gitignore_content)
    print("✅ Created .gitignore")
    
    # Create README
    readme_content = f"""# {project_name}

FastAPI backend built with uv

## Setup

1. Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Run the server:
```bash
uv run uvicorn main:app --reload --port 8000
```

4. Access the API:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Testing

Run tests:
```bash
uv run pytest
```

With coverage:
```bash
uv run pytest --cov=. --cov-report=html
```
"""
    (project_path / "README.md").write_text(readme_content)
    print("✅ Created README.md")
    
    print(f"\n✨ Project '{project_name}' initialized successfully!")
    print(f"\nNext steps:")
    print(f"1. cd {project_name}")
    print(f"2. cp .env.example .env")
    print(f"3. Edit .env with your API keys")
    print(f"4. uv sync")
    print(f"5. uv run uvicorn main:app --reload")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init_project.py <project_name> [target_directory]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    target_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    init_project(project_name, target_dir)
