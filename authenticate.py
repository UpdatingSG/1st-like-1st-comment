import os
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

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

            response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=1  # Limit to 1 most recent video
            ).execute()

            print(response)

            # Check if there's a new video
            if response["items"]:
                video_id = response["items"][0]["snippet"]["resourceId"]["videoId"]
                youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "channelId": channel_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": comment_text
                                }
                            },
                            "videoId": video_id,
                    }
                    }
                ).execute()
                print("Commented on the new video.")

                youtube.videos().rate(
                    id=video_id,
                    rating="like"
                ).execute()
                print("Liked the new video.")

            time.sleep(60)  # Check every minute
        except googleapiclient.errors.HttpError as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    youtube = authenticate()
    channel_id = "UCX370DhCjV5zmmbJN0saqxg"  #Replace with the channel ID you want to monitor# 
    comment_text = "bhai axi video banaya kr"  # Replace with the comment you want to post
    monitor_and_comment(youtube, channel_id, comment_text)
    print("Successfully authenticated with YouTube Data API.")
