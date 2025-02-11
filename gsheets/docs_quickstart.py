from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from markdown2 import markdown
import io

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


def create_doc_from_markdown(
    service, title, markdown_content, users=["bianderson@linkedin.com"]
):
    """
    Converts the markdown string into html, then turns into in a bytes object, then uploads directly to Google Drive like it was a file upload.
    """
    # Shrink the headers by one level
    markdown_string = markdown_content.replace("# ", "## ")
    # Convert markdown to html
    html = markdown(markdown_string)
    # Create a new Google Doc
    file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    media = MediaIoBaseUpload(
        io.BytesIO(html.encode("utf-8")), mimetype="text/html", resumable=True
    )
    # Upload the document to Google Drive
    file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    doc_id = file.get("id")
    doc_url = f"https://docs.google.com/document/d/{doc_id}"
    # Share with user(s)
    for user in users:
        permission = {"type": "user", "role": "writer", "emailAddress": user}
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission,
            fields="id",
            sendNotificationEmail=False,
        ).execute()
    return doc_url


if __name__ == "__main__":
    title = "Building AI Products, v2"
    url = create_doc_from_markdown(docs_service, title, markdown_string)
    print(f"Created and shared document with title: {title}")
    print(url)
