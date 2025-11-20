from fastapi import APIRouter, HTTPException
from scrap.scrap import scrape_article, scrape_all_articles
from agents.cards import create_cards
from agents.mindmap import create_mindmap
from agents.pyq import create_pyq
from agents.analyse import extract_sections
from services.db_service import save_daily_content, get_daily_content, get_all_dates
import json

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
async def generate_and_save_content(date: str):
    """
    Scrape, analyze, and generate all content for a date, then save to database.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        
    Returns:
        Success message with date
    """
    try:
        # Step 1: Scrape articles
        article = scrape_all_articles(date=date)
        
        # Step 2: Extract sections
        sections = extract_sections(article_text=article)
        
        if not sections:
            raise HTTPException(status_code=400, detail="No sections extracted from article")
        
        # Step 3: Generate content for each section
        all_cards = []
        all_mindmaps = []
        all_pyqs = {"prelims": [], "mains": []}
        
        for section in sections:
            # Get section content (it's an array, so join it)
            section_content = section.get("content", [])
            if isinstance(section_content, list):
                section_text = "\n".join(section_content)
            else:
                section_text = str(section_content)
            
            # Generate cards
            section_cards = create_cards(content=section_text)
            if isinstance(section_cards, list):
                all_cards.extend(section_cards)
            
            # Generate mindmap
            mindmap = create_mindmap(content=section_text)
            all_mindmaps.append(mindmap)
            
            # Generate PYQ
            pyq = create_pyq(content=section_text)
            if isinstance(pyq, dict):
                if "prelims" in pyq and isinstance(pyq["prelims"], list):
                    all_pyqs["prelims"].extend(pyq["prelims"])
                if "mains" in pyq and isinstance(pyq["mains"], list):
                    all_pyqs["mains"].extend(pyq["mains"])
        
        # Step 4: Save to database
        success = save_daily_content(
            date=date,
            sections=sections,
            cards=all_cards,
            mindmap={"mindmaps": all_mindmaps},  # Store all mindmaps
            pyq=all_pyqs
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save content to database")
        
        return {
            "message": "Content generated and saved successfully",
            "date": date,
            "sections_count": len(sections),
            "cards_count": len(all_cards),
            "mindmaps_count": len(all_mindmaps),
            "prelims_count": len(all_pyqs["prelims"]),
            "mains_count": len(all_pyqs["mains"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")


@router.get("/scrape/{date}")
async def scrape_content(url: str):
    """
    Scrape content from a URL (legacy endpoint).
    """
    output_file = scrape_article(url=url, output_file="date")
    with open(output_file, "r") as f:
        content = f.read()
    return {"content": content}