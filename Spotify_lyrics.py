!pip install youtube_dl

!pip install spotipy

!pip install beautifulsoup4

import os
import re
import spotipy
from youtube_dl import YoutubeDL
from urllib import request as rq
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup

file = open('spotify_credentials.txt', 'r').read().splitlines()
client_id, client_secret = file[0], file[1]

class Downloader:
    __CLIENT_ID =client_id 
    __CLIENT_SECRET = client_secret

    def __init__(self, pl_uri):
        self.auth_manager = SpotifyClientCredentials(client_id=self.__CLIENT_ID, client_secret=self.__CLIENT_SECRET)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        self.pl_uri = pl_uri

    def get_playlist_details(self):
        offset = 0
        pl_name = self.sp.playlist(self.pl_uri)["name"]
        pl_items = self.sp.playlist_items(self.pl_uri, offset=offset,
                                          fields="items.track.name,items.track.artists.name, total",
                                          additional_types=["track"], )["items"]

        pl_tracks = []
        while len(pl_items) > 0:
            for item in pl_items:
                track_name = item["track"]["name"]
                artist_name = item["track"]["artists"][0]["name"]
                pl_tracks.append(f"{artist_name}-{track_name}") #.encode(encoding='UTF-8',errors='strict'))

            offset = (offset + len(pl_items))
            pl_items = self.sp.playlist_items(
                self.pl_uri,
                offset=offset,
                fields="items.track.name,items.track.artists.name, total",
                additional_types=["track"],)["items"]
        return pl_tracks

    def get_links(self, pl_tracks):
        links = []
        for track in pl_tracks:
            wykonawca = track.split("-")[0].replace(" ","+")
            tytul = track.split("-")[1].replace(" ","+")
            url = f"https://www.tekstowo.pl/szukaj,wykonawca,{wykonawca},tytul,{tytul}.html"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                propositions = ['https://www.tekstowo.pl'+td.attrs['href'] for i,td in enumerate(soup.find('h2', text='Znalezione utwory:').parent.find_all('a')) if i<5 and 'piosenka' in td.attrs['href']]
                links.append([propositions[0], wykonawca, tytul])
            except:
                try: #try different way
                    wykonawca = track.split("-")[0].replace(" ","_")
                    tytul = track.split("-")[1].replace(" ","_")
                    url = f"https://www.tekstowo.pl/piosenka,{wykonawca},{tytul}.html"
                    #Check if exists:
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    if '404 - Nie ma takiego pliku! - www.tekstowo.pl' in str(soup.contents):
                        continue
                    else:
                        links.append([url, wykonawca, tytul])
                except:
                    print("Lyrics not found for track:", url)
        return links

    def get_lyrics(self, links):
        for link in links:
            page = requests.get(link[0])
            soup = BeautifulSoup(page.content, 'html.parser')
            text = str(soup.find_all("div", {"class": "song-text"}))
            pos0 = text.find('Tekst piosenki:</h2>')
            pos1 = text.find('adv-home')
    #         print(pos0, pos1)
            result = re.match(r'\s\s+', '\t')
            text = text[pos0+20:pos1-12].replace("  ","").replace("<br>", "").replace("<br/>", "")
            r = re.compile(r"^\s+", re.MULTILINE)
            text = r.sub("", text)
            removelist = "=. \n"
            text = re.sub(r'[^\w'+removelist+']', ' ',text)
            text ="\n".join([ll.rstrip() for ll in text.splitlines() if ll.strip()])
            file_name = f'teksty/{link[1].replace("+"," ").replace("/","")}-{link[2].replace("+"," ").replace("/","")}.txt'
            try:
                file = open(file_name, 'w')
                file.write(text)
                file.close()
            except:
                print(file_name)
            

if __name__ == "__main__":
    downloader = Downloader('5AJycjgmpmYYYga2enTHSG')
    tracks = downloader.get_playlist_details()
    links = downloader.get_links(tracks)
    lyrics = downloader.get_lyrics(links)

len(tracks), tracks[0:2]
