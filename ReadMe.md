# HackNU backend service

## Project structure
- app --> fastapi main folder
    - ai_models --> models for ai (genAI, ml, anything)
    - clients --> redis, minio, or smth else
    - controllers --> interaction with db, client (redis, minio, other services)
    - db --> db models or queries
    - helpers --> some helpers functions
    - routers --> http routes of project
    main.py --> main.py file that initialize app
    db_scheme.py --> scheme for db (for alembic)
    config.py --> some api keys or anything else
- jobs --> train.py or smth else
- notebooks -> some ipynb for ml
requirements.txt --> pip install -r requirements.txt

Please set up virtual environment
```
python -m venv venv
pip install -r requirements.txt
```