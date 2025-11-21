import time
from scrap.scrap import scrape_article, scrape_all_articles
from agents.cards import create_cards
from agents.mindmap import create_mindmap
from agents.pyq import create_pyq
from agents.analyse import extract_sections
from agents.review import review_all_content
from services.db_service import save_daily_content


MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def generate_and_save_content(date: str):
    """
    Scrape, analyze, and generate all content for a date, then save to database.
    
    Args:
        date: Date string in format "DD-MM-YYYY" (e.g., "13-10-2025")
        
    Returns:
        Dict with success status and content counts, or None on failure
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Step 1: Scrape articles
            article = scrape_all_articles(date=date)
            
            # Step 2: Extract sections
            sections = extract_sections(article_text=article)
            
            if not sections:
                print(f"No sections extracted from article for date {date}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
            
            # Step 3: Generate content for each section
            all_cards = []
            all_mindmaps = []
            all_pyqs = {"prelims": [], "mains": []}
            
            for section_index, section in enumerate(sections):
                # Get section content (it's an array, so join it)
                section_content = section.get("content", [])
                if isinstance(section_content, list):
                    section_text = "\n".join(section_content)
                else:
                    section_text = str(section_content)
                
                # Get section title for reference
                section_title = section.get("title", f"Section {section_index + 1}")
                
                # Generate cards with section reference
                section_cards = create_cards(content=section_text)
                if isinstance(section_cards, list):
                    for card in section_cards:
                        if isinstance(card, dict):
                            card["section_index"] = section_index
                            card["section_title"] = section_title
                    all_cards.extend(section_cards)
                
                # Generate mindmap with section reference
                mindmap = create_mindmap(content=section_text)
                if isinstance(mindmap, dict):
                    mindmap["section_index"] = section_index
                    mindmap["section_title"] = section_title
                all_mindmaps.append(mindmap)
                
                # Generate PYQ with section reference
                pyq = create_pyq(content=section_text)
                if isinstance(pyq, dict):
                    if "prelims" in pyq and isinstance(pyq["prelims"], list):
                        for prelim_q in pyq["prelims"]:
                            if isinstance(prelim_q, dict):
                                prelim_q["section_index"] = section_index
                                prelim_q["section_title"] = section_title
                        all_pyqs["prelims"].extend(pyq["prelims"])
                    if "mains" in pyq and isinstance(pyq["mains"], list):
                        for mains_q in pyq["mains"]:
                            if isinstance(mains_q, dict):
                                mains_q["section_index"] = section_index
                                mains_q["section_title"] = section_title
                        all_pyqs["mains"].extend(pyq["mains"])
            
            # Step 4: Review and correct all content
            print(f"Reviewing content for date {date}...")
            review_results = review_all_content(
                sections=sections,
                cards=all_cards,
                mindmaps=all_mindmaps,
                pyq=all_pyqs,
                original_text=article
            )
            
            # Extract corrected content
            corrected_sections = review_results["sections"]["corrected_sections"]
            corrected_cards = review_results["cards"]["corrected_cards"]
            corrected_mindmaps = [result["corrected_mindmap"] for result in review_results["mindmaps"]]
            corrected_pyq = review_results["pyq"]["corrected_pyq"]
            
            # Log review summary
            overall_review = review_results["overall_review"]
            print(f"Review completed: {overall_review['total_issues']} issues found, "
                  f"{overall_review['total_corrections']} corrections made, "
                  f"accuracy: {overall_review['average_accuracy']:.2%}")
            
            # Step 5: Save corrected content to database
            success = save_daily_content(
                date=date,
                sections=corrected_sections,
                cards=corrected_cards,
                mindmap={"mindmaps": corrected_mindmaps},  # Store all mindmaps
                pyq=corrected_pyq,
                overall_review=overall_review
            )
            
            if not success:
                print(f"Failed to save content to database for date {date}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
            
            return {
                "message": "Content generated and saved successfully",
                "date": date,
                "sections_count": len(corrected_sections),
                "cards_count": len(corrected_cards),
                "mindmaps_count": len(corrected_mindmaps),
                "prelims_count": len(corrected_pyq.get("prelims", [])),
                "mains_count": len(corrected_pyq.get("mains", [])),
                "review_summary": {
                    "total_issues": overall_review["total_issues"],
                    "total_corrections": overall_review["total_corrections"],
                    "average_accuracy": overall_review["average_accuracy"]
                }
            }
            
        except Exception as e:
            print(f"Error generating content for date {date} (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None
    
    return None


