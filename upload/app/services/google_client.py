import gspread
from google.oauth2.service_account import Credentials
from app.config import settings


class GoogleClientFactory:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    @classmethod
    def create_client(cls):
        credentials = Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=cls.SCOPES,
        )
        return gspread.authorize(credentials)