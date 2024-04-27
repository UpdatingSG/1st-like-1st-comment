import os
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime


def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", scopes
    ) #make sure to have your oauth credentials in client_secrets.json file
    credentials = flow.run_local_server()

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    return youtube

def monitor_and_comment(youtube, channel_id, comment_text):
    while True:
        try:
            response = youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            now = datetime.datetime.now(datetime.timezone.utc)
            print(now)
            # Calculate the start of today in ISO 8601 format
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            

            response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=1,  # Limit to 1 most recent video
            ).execute()

            today_videos = [item for item in response["items"] if datetime.datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc) >= today_start]

            print(today_videos)

            # Check if there's a new video
            if today_videos:
                for i in range(0,70):
                    video_id = today_videos[0]["snippet"]["resourceId"]["videoId"]
                    youtube.commentThreads().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "channelId": channel_id,
                                "topLevelComment": {
                                    "snippet": {
                                        "textOriginal": comment_text + str(i)
                                    }
                                },
                                "videoId": video_id,
                        }
                        }
                    ).execute()
                    print("Commented on the new video." + comment_text + str(i))

                youtube.videos().rate(
                    id=video_id,
                    rating="like"
                ).execute()
                print("Liked the new video.")

                time.sleep(1)  # Check every minute
        except googleapiclient.errors.HttpError as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    youtube = authenticate()
    channel_id = "UCqdPP-1FIdmTX4u9QrT-87Q"  #Replace with the channel ID you want to monitor# 
    comment_text = "#MIVSDC Ishan kishan will score "  # Replace with the comment you want to post
    monitor_and_comment(youtube, channel_id, comment_text)
    print("Successfully authenticated with YouTube Data API.")

    # UCqdPP-1FIdmTX4u9QrT-87Q   F

    # UCK9Cv9sxfYZpgr3nYdqIhsA A
