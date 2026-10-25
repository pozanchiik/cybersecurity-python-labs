pip install -r requirements.txt
python -m labs.lab03.seed
uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
curl -i -X GET "http://127.0.0.1:8000/ping"
curl -i -X GET "http://127.0.0.1:8000/student"
curl -i -X GET "http://127.0.0.1:8000/categories"
curl -i -X POST "http://127.0.0.1:8000/records" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "V01-99",
    "title": "Тестова знахідка вебаудиту",
    "category_id": 1,
    "value": 8.5,
    "status": "new"
  }'
curl -i -X GET "http://127.0.0.1:8000/records?category_id=1&status=new&min_value=7.0&limit=5&offset=0"
curl -i -X PUT "http://127.0.0.1:8000/records/1" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "V01-01",
    "title": "Оновлена знахідка вебаудиту 01",
    "category_id": 1,
    "value": 9.5,
    "status": "in_progress"
  }'
curl -i -X DELETE "http://127.0.0.1:8000/records/1"
curl -i -X POST "http://127.0.0.1:8000/records/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "code": "V01-TEMP-FAIL",
      "title": "Новий перший елемент",
      "category_id": 1,
      "value": 4.0,
      "status": "new"
    },
    {
      "code": "V01-01",
      "title": "Дублікат коду",
      "category_id": 2,
      "value": 5.0,
      "status": "new"
    }
  ]'