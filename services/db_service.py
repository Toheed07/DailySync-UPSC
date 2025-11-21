from datetime import datetime
from typing import Dict, List, Optional
from config.db import db


def save_daily_content(date: str, sections: List[Dict], cards: List[Dict], 
                       mindmap: Dict, pyq: Dict, overall_review: Dict) -> bool:
    """
    Save all daily content (sections, cards, mindmap, pyq) to Firestore.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        sections: List of section dictionaries
        cards: List of card dictionaries
        mindmap: Mindmap dictionary
        pyq: PYQ dictionary with prelims and mains
        overall_review: Overall review dictionary
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert date to document ID (use date as-is for easy querying)
        doc_ref = db.collection("daily_content").document(date)
        
        # Prepare document data
        data = {
            "date": date,
            "sections": sections,
            "cards": cards,
            "mindmap": mindmap,
            "pyq": pyq,
            "overall_review": overall_review,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Save to Firestore
        doc_ref.set(data, merge=True)
        print(f"Successfully saved content for date: {date}")
        return True
        
    except Exception as e:
        print(f"Error saving content to database: {e}")
        return False


def get_daily_content(date: str) -> Optional[Dict]:
    """
    Fetch all daily content for a specific date.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        
    Returns:
        Dict with sections, cards, mindmap, pyq or None if not found
    """
    try:
        doc_ref = db.collection("daily_content").document(date)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            # Convert Firestore timestamps to ISO strings for JSON serialization
            if "created_at" in data and hasattr(data["created_at"], "isoformat"):
                data["created_at"] = data["created_at"].isoformat()
            if "updated_at" in data and hasattr(data["updated_at"], "isoformat"):
                data["updated_at"] = data["updated_at"].isoformat()
            return data
        else:
            print(f"No content found for date: {date}")
            return None
            
    except Exception as e:
        print(f"Error fetching content from database: {e}")
        return None


def get_all_dates() -> List[str]:
    """
    Get all available dates from the database.
    
    Returns:
        List of date strings
    """
    try:
        docs = db.collection("daily_content").stream()
        dates = [doc.id for doc in docs]
        return sorted(dates, reverse=True)  # Most recent first
        
    except Exception as e:
        print(f"Error fetching dates from database: {e}")
        return []


def get_content_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """
    Fetch content for a date range.
    
    Args:
        start_date: Start date in format "DD-MM-YYYY"
        end_date: End date in format "DD-MM-YYYY"
        
    Returns:
        List of content dictionaries
    """
    try:
        # Note: Firestore doesn't support range queries on document IDs directly
        # You might need to add a date field for proper range queries
        # For now, this fetches all and filters
        docs = db.collection("daily_content").stream()
        results = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_date = doc_data.get("date", doc.id)
            if start_date <= doc_date <= end_date:
                if "created_at" in doc_data and hasattr(doc_data["created_at"], "isoformat"):
                    doc_data["created_at"] = doc_data["created_at"].isoformat()
                if "updated_at" in doc_data and hasattr(doc_data["updated_at"], "isoformat"):
                    doc_data["updated_at"] = doc_data["updated_at"].isoformat()
                results.append(doc_data)
        
        return sorted(results, key=lambda x: x.get("date", ""), reverse=True)
        
    except Exception as e:
        print(f"Error fetching content by date range: {e}")
        return []


def delete_daily_content(date: str) -> bool:
    """
    Delete content for a specific date.
    
    Args:
        date: Date string in format "DD-MM-YYYY"
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        doc_ref = db.collection("daily_content").document(date)
        doc_ref.delete()
        print(f"Successfully deleted content for date: {date}")
        return True
        
    except Exception as e:
        print(f"Error deleting content from database: {e}")
        return False

