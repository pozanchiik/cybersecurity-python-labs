pip install -r requirements.txt
python -m labs.lab03.seed
uvicorn labs.lab03.main:app --reload