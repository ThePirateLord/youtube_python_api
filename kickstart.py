from __future__ import print_function

from httplib2 import Http
import os
import sys
import argparse

from apiclient import discovery
from apiclient.errors import HttpError
import oauth2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client import client, tools
import youtube_dl

from flask import Flask
from flask.ext import restful
app = Flask(__name__)
api = restful.Api(app)

SCOPES = 'https://www.googleapis.com/auth/youtube'
CLIENT_SECRET_FILE = 'client_secret.json'
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
APPLICATION_NAME = 'youtube_music'



try:
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags=None

'''
	Authenticate user ,collects user's credentials.
'''
def get_user_credentials():
	# cur_path = '/home/divyanshu/gitHub/my_projects/proj_youtube'
	_loc_ = os.path.realpath(
			os.path.join(os.getcwd(),os.path.dirname(__file__))
			)

	credential_dir = os.path.join(_loc_, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'youtube_music_cred.json')
	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else:
			credentials =  tools.run(flow, store)
		print ("Credentials is making......")
	return credentials


'''
This function retrieves user's defualt youtube's playlists[favorites, likes, uploads, watchHistory, watchLater].
'''
def users_youtube_related_playlists(youtube):
	channels_response = youtube.channels().list(
		part="contentDetails", 
		maxResults=50,
		mine=True
		).execute()
	# channel = channels_response["items"][0]
	related_playlists = channels_response["items"][0]['contentDetails']['relatedPlaylists']
	return related_playlists


'''
Returns ID of selected playlist from user's youtube related playlists.
'''
def playlist_id_from_related_playlists(related_playlists, playlist_name="watchHistory"):
		'''
		playlist_name = ['favorites', 'likes', 'uploads', 'watchHistory', 'watchLater']
		favorites = 0, likes = 1, uploads = 2, watchHistory = 3, watchLater = 4
		'''
		if playlist_name == 'favorites':
			playlist_id = related_playlists['favorites']
		elif playlist_name == 'likes':
			playlist_id = related_playlists['likes']
		elif playlist_name == 'uploads':
			playlist_id = related_playlists['uploads']
		elif playlist_name == 'watchHistory':
			playlist_id = related_playlists['watchHistory']
		elif playlist_name == 'watchLater':
			playlist_id = related_playlists['watchLater']
		else:
			print("400/Bad Choice")
		return playlist_id


'''
Retrieves every video of the playlist_id being passed.
'''
def retrieve_videos_from_playlist(youtube, playlist_id, next_page_token=None):
	playlists_item_response = youtube.playlistItems().list(
		part="snippet,contentDetails",
		playlistId=playlist_id,
		maxResults=49,
		pageToken=next_page_token
		).execute()

	index = 0
	results = []
	for video in playlists_item_response['items']:
		video_title = video['snippet']['title']
		video_id = video['contentDetails']['videoId']
		index += 1
		results.append({'index'			: index,
						'video_title'	: video_title,
						'video_id'		: video_id
						})
	# if "next_page_token" in playlists_item_response:
	# 	page_token = playlists_item_response["nextPageToken"]
	# 	results.extend(retrieve_videos_from_playlist(youtube, playlist_id, page_token));
	# 	print("---------------------------Results--------------------------------------")
	# 	print(results)
	# 	return results
	# else:
	# 	print("---------------------------Results--------------------------------------")
	# 	print(results)
	# 	return results
	print(results)
	return results


@app.route('/index')
def lets_kickstart():
	credentials 		= get_user_credentials()
	http 				= credentials.authorize(Http())
	youtube 			= discovery.build(API_SERVICE_NAME, API_VERSION, http=http)
	related_playlists 	= users_youtube_related_playlists(youtube)
	playlist_id 		= playlist_id_from_related_playlists(related_playlists)
	videos_details		= retrieve_videos_from_playlist(youtube, playlist_id)
	# return{'Chal gaya': 'code bc'}
	return ('Chal gaya code bc')

if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=True)