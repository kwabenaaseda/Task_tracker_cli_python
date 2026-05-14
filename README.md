# PROJECT URL : https://github.com/kwabenaaseda/Task_tracker_cli_python

# Task Tracker

A production-ready CLI task management application with PostgreSQL backend, Docker containerization, and comprehensive test coverage.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Task status management (TODO, IN_PROGRESS, DONE)
- ✅ PostgreSQL persistence with hybrid JSON caching
- ✅ Docker & Docker Compose for easy deployment
- ✅ Comprehensive pytest test suite
- ✅ Modular architecture (CLI → Logic → Data layers)
- ✅ Interactive CLI with formatted output

## Quick Start

### Using Docker (Recommended)

```bash
git clone https://github.com/kwabenaaseda/Task_tracker_cli_python.git
cd task_tracker_python
docker-compose up
```

Then in another terminal:
```bash
docker-compose exec app python -m src.main
```

### Local Setup

**Requirements:**
- Python 3.10+
- PostgreSQL 14+

**Installation:**
```bash
pip install -r requirements.txt
psql -U kwabenaaseda -d kwabenaaseda
python -m src.main
```

## Usage

add Learn Docker
✅ Task Added


list
ID  Description       Status    Created
─────────────────────────────────────────
1   Learn Docker      ☑️ TODO    2026-05-14


status 1 IN_PROGRESS
✅ Status Updated


list --progress
ID  Description       Status           Created
─────────────────────────────────────────────
1   Learn Docker      ⏳ IN_PROGRESS   2026-05-14


delete 1
✅ Task Deleted


clean
✅ All Tasks Cleared


## Architecture
src/
├── main.py           # CLI entry point
├── cli/
│   └── parser.py     # Command routing
├── logic/
│   └── task.py       # Business logic
└── data/
└── repository.py # PostgreSQL & JSON layer

**Design Pattern:** Layered architecture with clear separation of concerns.
- **CLI Layer:** Argument parsing, formatting
- **Logic Layer:** Business rules, validation
- **Data Layer:** PostgreSQL queries, JSON caching

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_task.py::test_create_task -v
```

## Technical Decisions

### PostgreSQL + JSON Cache (Hybrid Approach)
- **Writes:** Always go to PostgreSQL (source of truth)
- **Reads:** Come from JSON cache (performance)
- **Trade-off:** Eventual consistency for speed

### Docker Containerization
- Ensures reproducibility across machines
- No local PostgreSQL installation needed
- One-command deployment

### Modular Architecture
- Easy to test (mock data layer)
- Easy to extend (add new commands)
- Easy to port (rebuild logic in other languages)

## What I Learned

- **PostgreSQL:** Connection pooling, parameterized queries, transactions
- **Testing:** Pytest fixtures, test isolation, mocking
- **Docker:** Dockerfile, docker-compose, networking, health checks
- **Python:** Async patterns (used in logic layer), type hints, context managers
- **System Design:** Layered architecture, separation of concerns, caching strategies

## Future Enhancements

- [ ] REST API with FastAPI
- [ ] Web UI (React/Vue)
- [ ] Mobile app (React Native)
- [ ] User authentication
- [ ] Task priorities and due dates
- [ ] Task tags and filtering
- [ ] Export to CSV/JSON

## Project Stats

- **Lines of Code:** ~500 (core logic)
- **Test Coverage:** 4 integration tests
- **Build Time:** < 1 minute
- **Deployment:** Single command (docker-compose up)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10 |
| Database | PostgreSQL 14 |
| Testing | pytest |
| Containerization | Docker & Docker Compose |
| CLI | argparse (standard library) |


## License

MIT License - Feel free to use this as a reference or learning material.

---
