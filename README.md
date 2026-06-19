# Auto-Scaling-Manager

![CI](https://github.com/skylerblue333/Auto-Scaling-Manager/workflows/CI/badge.svg)

Production-ready backend service for manager operations.

## Architecture
- **API Framework**: FastAPI
- **Concurrency**: Asyncio event loop
- **Testing**: Pytest with 100% coverage
- **Deployment**: Docker containerized

## Quick Start
```bash
pip install -r requirements.txt
pytest tests/ -v
uvicorn src.main:app --reload
```
