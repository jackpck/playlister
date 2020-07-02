'''
create data/db in /System/Volumes/Data
For MacOS, run mongo daemon: sudo mongod --dbpath /System/Volumes/Data/data/db
For Windows, run mongo daemon: mongod --dbpath C:/data/db
'''

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os


def video_url_creator(id_lst):
    videos = []
    for vid_id in id_lst:
        # We know that embedded YouTube videos always have this format
        video = 'https://youtube.com/embed/' + vid_id
        videos.append(video)
    return videos

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Playlister')
client = MongoClient(host=host)
db = client.get_default_database()
playlists = db.playlists

app = Flask(__name__)

@app.route('/')
def playlists_index():
    """Show all playlists."""
    return render_template('playlists_index.html', playlists=playlists.find())

@app.route('/playlists/new')
def playlists_new():
    """Create a new playlist."""
    return render_template('playlists_new.html')

@app.route('/playlists/<playlist_id>/edit')
def playlist_edit(playlist_id):
    """Show the edit form for a playlist."""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    return render_template('playlists_edit.html',playlist=playlist)

@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlist_delete(playlist_id):
    """Delete one playlist."""
    playlists.delete_one({'_id':ObjectId(playlist_id)})
    return redirect(url_for('playlists_index'))

@app.route('/playlists', methods=['POST'])
def playlists_submit():
    """Submit a new playlist. A placeholder of sort. Only deal with db.
     Is never displayed. """

    video_ids = request.form.get('video_ids').split()
    videos = video_url_creator(video_ids)
    playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos':videos,
        'video_ids':video_ids
    }
    playlists.insert_one(playlist)
    return redirect(url_for('playlists_index'))

@app.route('/playlists/<playlist_id>')
def playlist_show(playlist_id):
    """Show a single playlist"""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    return render_template('playlists_show.html',playlist=playlist)

@app.route('/playlists/<playlist_id>', methods=['POST'])
def playlist_update(playlist_id):
    """Submit an edited playlist. """
    video_ids = request.form.get('video_ids').split()
    videos = video_url_creator(video_ids)
    # create our updated playlist
    updated_playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': videos,
        'video_ids': video_ids
    }
    # set the former playlist to the new one we just updated/edited
    playlists.update_one(
        {'_id': ObjectId(playlist_id)},
        {'$set': updated_playlist})
    # take us back to the playlist's show page
    return redirect(url_for('playlist_show', playlist_id=playlist_id))


if __name__ == '__main__':
    app.run(debug=True)