import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import app
import json

@pytest.fixture
def client():
    app.config["TESTING"]=True
    return app.test_client()

def test_no_player_id_or_token(client):
    response = client.get("/get_scores/")
    assert response.status_code == 404 #such route does not exist in our API

def test_no_player_id(client):
    headers = {"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZ2FtZWJ1c19hcGkiXSwidXNlcl9uYW1lIjoiZC52YW5laWpsQHN0dWRlbnQuZm9udHlzLm5sIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIiwidHJ1c3QiXSwiZXhwIjoxNzY3OTQyODcxLCJhdXRob3JpdGllcyI6WyJERVYiLCJVU0VSIl0sImp0aSI6InQ3OUZnQm4xaGprX3BnSG1CQ0NPOVVXc3BEayIsImNsaWVudF9pZCI6ImdhbWVidXNfYmFzZV9hcHAifQ.Ey9WBijTTCoB5WdmiWb_pfrBOPUHxSh0b8jGlWzPqK3ahTbkGdGvG5alm3Tl75cse3RVSq7Y-XttuoStQSXMJpLTEMjXFCuqEbkp-wvnl-xepguWutGECaFJy0XxlGUTOfBYe8Zahl7sN6TTH3h0aZYw2LD60qHEPdcL3bpeW0NBcq4um_50E-0mHdgtxQWzblVy6fr5itjmI-4azSlr2XOYyamNYNmsjfnfHQPNq1RYhFpy-ewXc7s1svFh9EhOMd5OcWD0ht5cDRcm6Iqz6T06W6az05fIWlXN2Q9k5SzPu0Ct0YBkzr4EXxwXyJeT-nWZnCbi30wYwEd78FtsJw"}
    response = client.get("/get_scores/", headers=headers)
    assert response.status_code == 404 #such route does not exist in our API

def test_no_token(client):
    response = client.get("/get_scores/993")
    assert response.status_code == 500

def test_with_player_id_and_token(client):
    headers = {"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZ2FtZWJ1c19hcGkiXSwidXNlcl9uYW1lIjoiZC52YW5laWpsQHN0dWRlbnQuZm9udHlzLm5sIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIiwidHJ1c3QiXSwiZXhwIjoxNzY3OTQyODcxLCJhdXRob3JpdGllcyI6WyJERVYiLCJVU0VSIl0sImp0aSI6InQ3OUZnQm4xaGprX3BnSG1CQ0NPOVVXc3BEayIsImNsaWVudF9pZCI6ImdhbWVidXNfYmFzZV9hcHAifQ.Ey9WBijTTCoB5WdmiWb_pfrBOPUHxSh0b8jGlWzPqK3ahTbkGdGvG5alm3Tl75cse3RVSq7Y-XttuoStQSXMJpLTEMjXFCuqEbkp-wvnl-xepguWutGECaFJy0XxlGUTOfBYe8Zahl7sN6TTH3h0aZYw2LD60qHEPdcL3bpeW0NBcq4um_50E-0mHdgtxQWzblVy6fr5itjmI-4azSlr2XOYyamNYNmsjfnfHQPNq1RYhFpy-ewXc7s1svFh9EhOMd5OcWD0ht5cDRcm6Iqz6T06W6az05fIWlXN2Q9k5SzPu0Ct0YBkzr4EXxwXyJeT-nWZnCbi30wYwEd78FtsJw"}
    response = client.get("/get_scores/993", headers=headers)
    assert response.status_code == 200

