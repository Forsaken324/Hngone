from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    n = int(n)
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    n = int(n)
    return n == sum(i for i in range(1, n) if n % i == 0)

def is_armstrong(n: int) -> bool:
    n = int(n)
    return n == sum(int(d) ** len(str(n)) for d in str(n))

# API Endpoint
@app.get("/api/classify-number", response_model=NumberClassification)
def classify_number(number : str | None = Query(None)):
    if number is None:
        return JSONResponse(status_code=400, content={"number": None, "error": True})

    try:
        validate_number = int(number)
    except ValueError:
        return JSONResponse(status_code=400, content={"number" : number, "error" : True})

    
        # Validate number
    digit_sum = sum(int(d) for d in str(int(abs(number))))
    prime = is_prime(number)
    perfect = is_perfect(number)
    armstrong = is_armstrong(number)
    parity = "odd" if int(number) % 2 else "even"

    properties = [parity]
    if armstrong:
        properties.insert(0, "armstrong")

        # Fetch fun fact
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

