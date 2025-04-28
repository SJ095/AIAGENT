

import re
import asyncio

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
import asyncio
from google_play_scraper import reviews, search, Sort
import ollama
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

# Define the Pydantic model for the incoming request
class AppNameRequest(BaseModel):
    app_name: str

# Allow cross-origin requests from the frontend
origins = [
    "http://localhost:3000",  # Replace with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response model for sentiment analysis results
class SentimentResponse(BaseModel):
    average_sentiment: float
    review_count: int
    reviews: List[str]
    sentiment_scores: List[float]  # Add sentiment scores for each review

# Initialize the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# async function to analyze sentiment
async def analyze_sentiment(review_text: str) -> float:
    max_length = 512
    truncated_review = review_text[:max_length]
    prompt = f"""Analyze the sentiment of the following review.Respond with ONLY a single floating-point number between -1.0(very negative) and 1.0 ( very positive).Do not include explanations or any other text.
Review: "{truncated_review}"
Sentiment Score:"""
    try:
        model = "mistral"  # Model to use
        logger.debug(f"Sending review (truncated) to Ollama: {truncated_review[:100]}...")

        response = await asyncio.to_thread(
            ollama.chat,
            model=model, 
            messages=[{"role": "user", "content": prompt}]
        )

        logger.debug(f"Full Ollama response object: {response}")

        if not response or 'message' not in response or 'content' not in response['message']:
            logger.error("Unexpected Ollama response structure")
            return None
        
        content = response['message']['content'].strip()

        logger.info(f"Ollama raw response content for review '{truncated_review[:50]}...': '{content}'")

        match = re.search(r"([-+]?\d*\.?\d+)", content)

        if match:
            extracted_text = match.group(1)
            logger.debug(f"Regex matched text: '{extracted_text}'")
            try:
                score = float(extracted_text)
                clamped_score = max(-1.0, min(1.0, score))

                if score != clamped_score:
                    logger.debug(f"Score clamped from {score} to {clamped_score}")
                return clamped_score
            except ValueError:
                logger.warning(f"ValueError:could not convert matched text '{extracted_text}' to float. Ollama raw content: '{content}'.Review: '{truncated_review[:50]}...'")
                return None
        else:
            logger.warning(f"Regex did not find a numerical score in ollama response: '{content}'.Review: '{truncated_review[:50]}...'")
            return None
    except Exception as e:
        logger.error(f"Exception during ollama call or processing for review '{truncated_review[:50]}...': {e}", exc_info=True)
        return None

# Endpoint to get sentiment for app reviews
@app.post("/get-sentiment", response_model=SentimentResponse)
async def get_sentiment(app_name_request: AppNameRequest):
    try:
        app_name = app_name_request.app_name.lower()

        search_results = search(app_name, lang='en', country='us')
        if not search_results:
            raise HTTPException(status_code=404, detail="App not found. Please try a different app name.")
        app_id = search_results[0]['appId']
        
        logger.info(f"App ID for {app_name}: {app_id}")
        
    except Exception as e:
        logger.error(f"Error in searching app: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search for app: {str(e)}")

    try:
        result, _ = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=100,
            filter_score_with=None
        )
        
        logger.info(f"Fetched {len(result)} reviews for app {app_name}")
        
    except Exception as e:
        logger.error(f"Error fetching reviews for {app_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reviews: {str(e)}")

    review_texts = [r['content'] for r in result if r['content']]

    if not review_texts:
        logger.warning(f"No reviews found for app {app_name}")
        raise HTTPException(status_code=404, detail="No reviews found for this app.")
    
    try:
        sentiments = await asyncio.gather(*(analyze_sentiment(text) for text in review_texts))
        logger.info(f"Sentiment analysis completed for {len(sentiments)} reviews")
    except Exception as e:
        logger.error(f"Error analyzing sentiments: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiments: {str(e)}")

    average_sentiment = sum(sentiments) / len(sentiments)
    
    logger.info(f"Average sentiment for {app_name}: {average_sentiment}")
    
    return SentimentResponse(
        average_sentiment=average_sentiment,
        review_count=len(review_texts),
        reviews=review_texts,
        sentiment_scores=sentiments
    )

# ----------------------------
# 🆕 AUTOCOMPLETE ENDPOINT
# ----------------------------

@app.get("/autocomplete")
async def autocomplete_apps(query: str = Query(..., min_length=1)):
    try:
        logger.info(f"Autocomplete query received: {query}")
        search_results = search(query, lang='en', country='us')
        suggestions = [app['title'] for app in search_results[:5]]  # Top 5 matches
        logger.debug(f"Suggestions: {suggestions}")
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error fetching autocomplete suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch autocomplete suggestions")
