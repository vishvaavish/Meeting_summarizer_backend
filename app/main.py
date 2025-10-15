from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow your specific Vercel domain (add preview too if you use it)
ALLOWED_ORIGINS = [
    "https://meeting-summarizer-s134.vercel.app",
    # optional: enable previews for your project
    # "https://meeting-summarizer-s134-git-main-<team>.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)