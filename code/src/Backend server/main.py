from fastapi import FastAPI
from routers import anamoly_detection, db_router, rule_router, create_rules
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(anamoly_detection.router)
app.include_router(db_router.router)
app.include_router(rule_router.router)
app.include_router(create_rules.router)

# Run the application (if needed for local testing)
if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
