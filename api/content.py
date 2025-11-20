from fastapi import APIRouter, HTTPException, BackgroundTasks
from scrap.scrap import scrape_article, scrape_all_articles
from agents.cards import create_cards
from agents.mindmap import create_mindmap
from agents.pyq import create_pyq
from agents.analyse import extract_sections
from services.db_service import save_daily_content, get_daily_content, get_all_dates
import json
from services.content import generate_and_save_content as generate_and_save_content_task

router = APIRouter()


@router.get("/content/{date}")
async def get_content_by_date(date: str):
    """
    Fetch all content (sections, cards, mindmap, pyq) for a specific date.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        
    Returns:
        Dict containing sections, cards, mindmap, pyq, and metadata
    """
    content = get_daily_content(date)
    
    if content is None:
        raise HTTPException(status_code=404, detail=f"No content found for date: {date}")
    
    return content


@router.get("/dates")
async def get_available_dates():
    """
    Get all available dates in the database.
    
    Returns:
        List of date strings
    """
    dates = get_all_dates()
    return {"dates": dates}


@router.post("/generate/{date}")
async def generate_and_save_content(date: str, background_tasks: BackgroundTasks):
    """
    Scrape, analyze, and generate all content for a date, then save to database.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        
    Returns:
        Success message with date
    """
    try:
        background_tasks.add_task(generate_and_save_content_task, date=date)
        
        return {
            "message": f"Starting generation and saving content for date {date}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")


