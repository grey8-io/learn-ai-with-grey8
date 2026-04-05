# Rubric — FastAPI AI Backend

| Criterion | Points | Description |
|---|---|---|
| Pydantic models defined correctly | 20 | PredictRequest, PredictResponse, BatchRequest, BatchResponse with correct fields and types |
| GET /health endpoint works | 15 | Returns {"status": "ok"} with 200 status |
| POST /predict accepts and returns data | 20 | Validates PredictRequest, calculates confidence, returns PredictResponse |
| GET /models returns list | 15 | Returns list of available model names |
| POST /batch processes multiple texts | 20 | Handles batch input, returns results and count |
| Code quality | 10 | Clean app factory pattern, proper type hints, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
