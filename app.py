import json
from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import streamlit as st


# Streamlit Header
st.header("Google Indexing API - Overdose", divider='rainbow')


# Let users upload their secrets, which is a json file
# uploaded_file = st.file_uploader("Upload your secrets (JSON file)", type="json")
# if uploaded_file is not None:
#     secrets = json.load(uploaded_file)
#     service_account_info = secrets
#     credentials = service_account.Credentials.from_service_account_info(
#         service_account_info, scopes=["https://www.googleapis.com/auth/indexing"]
#     )
#     google_client = build("indexing", "v3", credentials=credentials)


# built-in secrets in Streamlit 
secrets = st.secrets

service_account_info = {
    "type": secrets["type"],
    "project_id": secrets["project_id"],
    "private_key_id": secrets["private_key_id"],
    "private_key": secrets["private_key"],
    "client_email": secrets["client_email"],
    "client_id": secrets["client_id"],
    "auth_uri": secrets["auth_uri"],
    "token_uri": secrets["token_uri"],
    "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": secrets["client_x509_cert_url"],
}

credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=["https://www.googleapis.com/auth/indexing"]
)

google_client = build("indexing", "v3", credentials=credentials)


# Use file
st.markdown("## Steps:")
steps = ''':one: Add 'seo-admin@darren-indexing-api.iam.gserviceaccount.com' as a delegated owner in Google Search Console for the website you'd like to submit

:two: Provide a list of URL you'd like to request indexing

:three: Submit
'''
st.markdown(steps)


urls_input = st.text_area("Enter URLs you'd like to submit, one URL per line")
submit_button = st.button("Submit")

if submit_button and urls_input:
    urls = urls_input.strip().split("\n")

    def submit_urls(urls):
        responses = []
        for url in urls:
            try:
                response = google_client.urlNotifications().publish(
                    body={"url": url, "type": "URL_UPDATED"}
                ).execute()
                responses.append((url, response))
            except HttpError as e:
                responses.append((url, e))
        return responses

    responses = submit_urls(urls)

    for url, response in responses:
        if isinstance(response, HttpError):
            error_message = response.content.decode("utf-8")
            if "Permission denied. Failed to verify the URL ownership" in error_message:
                st.error("Permission denied. Failed to verify the URL ownership. Please add 'seo-admin@darren-indexing-api.iam.gserviceaccount.com' as an 'Owner' in Google Search Console.")
            else:
                st.error(f"Error Message: {error_message}")
                st.error("Please contact Darren Huang for assistance.")
        else:
            notify_time_str = response.get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "")
            notify_time = datetime.strptime(notify_time_str.split('.')[0].rstrip('Z'), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            notify_time = notify_time.replace(microsecond=0)

            st.success(f"{url} | URL submitted successfully at {notify_time}.")
