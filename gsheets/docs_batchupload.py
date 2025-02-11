from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from markdown2 import markdown

# First, our markdown string -- our Enterprise AI LP
with open("Building_AI_Products.md", "r") as f:
    markdown_string = f.read()

# SCOPES specifies which Google APIs you want to authorize access to
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]
# Our credentials; I got this from following this tutorial from LI: https://iwww.corp.linkedin.com/wiki/cf/pages/viewpage.action?spaceKey=CIT&title=Service+Accounts+for+Google+APIs
SERVICE_ACCOUNT_FILE = ".service_credentials.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Create both Docs and Drive services; Docs to create the document, Drive to share it
docs_service = build("docs", "v1", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)

# Create document
body = {
    "title": "Building_AI_Products",
}
document = docs_service.documents().create(body=body).execute()
doc_id = document.get("documentId")

# Now do a batchupload to upload our markdown string
requests = [
    {
        "insertText": {
            "location": {"index": 1},
            "text": markdown_string,
        }
    }
]

docs_service.documents().batchUpdate(
    documentId=doc_id, body={"requests": requests}
).execute()


# Create permission for your email
def share_doc(email):
    permission = {"type": "user", "role": "writer", "emailAddress": email}
    drive_service.permissions().create(
        fileId=doc_id, body=permission, fields="id", sendNotificationEmail=False
    ).execute()


# Share with your email
share_doc("bianderson@linkedin.com")  # Replace with your email

print(f"Created and shared document with title: {document.get('title')}")
print(f"Document URL: https://docs.google.com/document/d/{doc_id}")
