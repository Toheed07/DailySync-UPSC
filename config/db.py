from google.cloud import firestore
from dotenv import load_dotenv
import os

load_dotenv()

project_id = os.getenv("PROJECT_ID")

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
db = firestore.Client(project=project_id)