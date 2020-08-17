# -*- coding: utf-8 -*-
"""Copy of Spotify-Top200-class.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1s8EAsYKMxgifu3Ey5W0ObgJ3w8SqP1t3
"""

pip install spotipy

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from urllib.request import Request, urlopen

import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

## first class: extract all countries and date that can be selected in Spotify Top 200 Charts website, this is for parameters used in the second class

class get_parameter():

    def get_country(self):
      web='https://spotifycharts.com/regional/global/weekly/latest'
      req = Request(web, headers={'User-Agent': 'Mozilla/5.0'})
      webpage = urlopen(req).read()
      soup = BeautifulSoup(webpage, 'html.parser')
      t1=soup.find_all('div',attrs={'data-type':'country'})[0].find_all('li')
      country_nm=[i.get_text() for i in t1]
      t2=[i.attrs for i in t1]
      country_cd=[i['data-value'] for i in t2]
      country=pd.DataFrame({'country_name':country_nm,'country_code':country_cd})
      return country
    
    def get_date(self):
      web='https://spotifycharts.com/regional/global/weekly/latest'
      req = Request(web, headers={'User-Agent': 'Mozilla/5.0'})
      webpage = urlopen(req).read()
      soup = BeautifulSoup(webpage, 'html.parser')
      t3=soup.find_all('div',attrs={'data-type':'date'})[0].find_all('li')
      t4=[i.attrs for i in t3]
      date_cd=[i['data-value'] for i in t4]
      return date_cd

## second class: this class includes all methods that can be used to scrape Top 200 charts and extract track popularity, 
## track audio feature and track related artists information through Spotify API

class SpotifyTop200():

    # sequence to extract all the data properly: top_200_chart >> track_popularity >> [artist_info,audio_feature]
    # client_id and client_secret refer to the Spotify app id and secret

    def __init__(self,country_code,date,client_id,client_secret):
      self.country_code=country_code
      self.date=date
      self.client_id=client_id
      self.client_secret=client_secret
    
    def top_200_chart(self):
      url='https://spotifycharts.com/regional/'+self.country_code+'/weekly/'+self.date
      req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
      webpage = urlopen(req).read()
      soup=BeautifulSoup(webpage, 'html.parser')

      info1=soup.find_all('tbody')
      info2=info1[0].find_all('tr')

      table=[]
      tracks_url_list=[]
      for i in info2:
        content=i.find_all('td')
        for j in content:
          line1=[i.get_text() for i in content]
          line2=[]
          for i in line1:
            line2.extend(i.split('\n'))
            line2=[i for i in line2 if len(i)>0]

          row=[]
          for k in line2:
            if k.startswith('by'):
              k=re.findall('by\s(.+)',k)
              row.extend(k)
            else: row.append(k)

      ## add country code
          row.append(self.country_code)
      ## add date
          row.append(self.date) 
      ## add track url,track id
          tracks_url=content[0].find_all('a')[0].get('href',None)
          row.append(tracks_url)
     
          tracks_id=re.findall('.+track/(.+)',tracks_url)     
          row.extend(tracks_id)

        table.append(row)
        tracks_url_list.append(tracks_url)
        
      my_file='my_file_path'+'tracks_url_'+self.country_code+'_'+self.date+'.json'
      with open(my_file, 'w') as f:
        json.dump(tracks_url_list, f)

      return table

    def track_popularity(self):
      my_file='my_file_path'+'tracks_url_'+self.country_code+'_'+self.date+'.json'
      try:
        with open(my_file, 'r') as openfile:
          tracks_url_list=json.load(openfile)
      except:
        print('important file missing, run "top_200_chart method" first')
      my_client_id=self.client_id
      my_client_secret=self.client_secret
      client_credentials_manager = SpotifyClientCredentials(client_id = my_client_id, client_secret = my_client_secret)
      sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
      track_pop=[]
      for i in tracks_url_list:
        row={}
        row['track_id']=sp.track(i)['id']
        row['track_popularity']=sp.track(i)['popularity']
        track_pop.append(row)

      artist_track={}
      artist_track['artist_ids']=[sp.track(i)['artists'][0]['id'] for i in tracks_url_list]
      artist_track['track_ids']=[sp.track(i)['id'] for i in tracks_url_list]

      my_file2='my_file_path'+'artist_track_'+self.country_code+'_'+self.date+'.json'
      with open(my_file2, 'w') as f:
        json.dump(artist_track, f)

      return track_pop

    def artist_info(self):
      my_file2='my_file_path'+'artist_track_'+self.country_code+'_'+self.date+'.json'
      try:
        with open(my_file2, 'r') as openfile:
          artist_track=json.load(openfile)
      except:
        print('important file missing, run "track_popularity method" first')
      my_client_id=self.client_id
      my_client_secret=self.client_secret
      client_credentials_manager = SpotifyClientCredentials(client_id = my_client_id, client_secret = my_client_secret)
      sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
      artist_ids=artist_track['artist_ids']
      track_ids=artist_track['track_ids']
      artist_idx=['name','followers','genres','popularity']
      artists_info=[]
      for i in range(len(artist_ids)):
        content=sp.artist(artist_ids[i])
        artist={}
        artist['artist_id']=artist_ids[i]
        for k in artist_idx:
          if type(content[k])==list and len(content[k])==0:
            artist[k]='-'
          elif type(content[k])==dict:
            artist[k]=content[k]['total']
          else:
            artist[k]=content[k]
          
          artist['track_id']=track_ids[i]
  
        artists_info.append(artist)
      return artists_info
    
    def audio_features(self):
      my_file2='my_file_path'+'artist_track_'+self.country_code+'_'+self.date+'.json'
      try:
        with open(my_file2, 'r') as openfile:
          artist_track=json.load(openfile)
      except:
        print('important file missing, run "track_popularity method" first')
      track_ids=artist_track['track_ids']
      my_client_id=self.client_id
      my_client_secret=self.client_secret
      client_credentials_manager = SpotifyClientCredentials(client_id = my_client_id, client_secret = my_client_secret)
      sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
      feature_idx=['acousticness','danceability','energy','instrumentalness','liveness','loudness','speechiness','valence','tempo']
      features=[]
      for i in track_ids:
        f={}
        f['track_id']=i
        content=sp.audio_features(i)
        for j in feature_idx:
          f[j]=content[0][j]
          
        features.append(f)
      
      return features

if __name__=="__main__":
  #spotify_parameter=get_parameter()
  #sptify_200=SpotifyTop200()

  pass