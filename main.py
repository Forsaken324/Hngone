from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract the invalid value from the request URL
    invalid_number = request.query_params.get("number", None)
    return JSONResponse(
        status_code=400,
        content={"number": invalid_number, "error": True}
    )

# Response model
class NumberClassification(BaseModel):
    number: int
    is_prime: bool
    is_perfect: bool
    properties: list[str]
    digit_sum: int
    fun_fact: str

# Helper functions
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    return n == sum(i for i in range(1, n) if n % i == 0)

def is_armstrong(n: int) -> bool:
    return n == sum(int(d) ** len(str(n)) for d in str(n))

# API Endpoint
@app.get("/api/classify-number", response_model=NumberClassification)
def classify_number(number: int | None = Query(None)):
    if number is None:
        return JSONResponse(status_code=400, content={"number": None, "error": True})

    digit_sum = sum(int(d) for d in str(abs(number)))
    prime = is_prime(number)
    perfect = is_perfect(number)
    armstrong = is_armstrong(number)
    parity = "odd" if number % 2 else "even"

    properties = [parity]
    if armstrong:
        properties.insert(0, "armstrong")

    response = requests.get(f"http://numbersapi.com/{number}/math?json")
    fun_fact = response.json().get("text", "No fun fact available.")

    return NumberClassification(
        number=number,
        is_prime=prime,
        is_perfect=perfect,
        properties=properties,
        digit_sum=digit_sum,
        fun_fact=fun_fact
    )
