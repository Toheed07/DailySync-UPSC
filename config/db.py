from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()

project_id = os.getenv("PROJECT_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to find credentials file
if credentials_path and os.path.exists(credentials_path):
    # Use explicitly provided credentials path
    cred_file = credentials_path
elif credentials_path:
    # Path provided but doesn't exist, try relative to project root
    cred_file = os.path.join(project_root, credentials_path)
    if not os.path.exists(cred_file):
        cred_file = None
else:
    cred_file = None

# If no explicit path, try common credential file names in project root
if not cred_file or not os.path.exists(cred_file):
    possible_cred_files = [
        os.path.join(project_root, "bnb-marathon-478215-6548ac978157.json"),
        os.path.join(project_root, "bnb-marathon-key.json"),
        os.path.join(project_root, "service-account-key.json"),
    ]
    
    for possible_file in possible_cred_files:
        if os.path.exists(possible_file):
            cred_file = possible_file
            # Set environment variable for other parts of the app
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
            break

# Initialize Firestore client
if cred_file and os.path.exists(cred_file):
    credentials = service_account.Credentials.from_service_account_file(cred_file)
    db = firestore.Client(project=project_id, credentials=credentials)
elif project_id:
    # Try default credentials (for cloud environments or gcloud auth)
    try:
        db = firestore.Client(project=project_id)
    except Exception as e:
        raise Exception(
            f"Firestore credentials not found. Please:\n"
            f"1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable, or\n"
            f"2. Place credentials JSON file in project root, or\n"
            f"3. Run 'gcloud auth application-default login'\n"
            f"Error: {e}"
        )
else:
    raise Exception("PROJECT_ID environment variable is required")