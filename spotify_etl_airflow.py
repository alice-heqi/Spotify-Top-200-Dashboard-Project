#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 19:57:55 2020

@author: alice.qi
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import pandas as pd
import numpy as np
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError
import json
from smart_open import open

pip install spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

## create dag and tasks

from airflow.operators.python_operator import PythonOperator

default_arguments={'owner':'alice_hq','start_date':datetime(2020, 8, 16)}

dag=DAG('spotify_etl',schedule_interval='@daily',catchup=False,default_args=default_arguments)

## cerate python function and python task

def artist_upload(bucket_name,s3_file_down,s3_file_up,access_key,secret_key,region,sp_client_id,sp_client_secret):
    session=boto3.Session(aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name=region)
    s3=session.resource('s3')
    bucket=s3.Bucket(bucket_name)
    down_obj=bucket.Object(key=s3_file_down)
    down_content=down_obj.get()['Body'].read().decode()
    json_content=json.loads(down_content)
    artist_ids=json_content['artist_ids']
    track_ids=json_content['track_ids']
    
    client_credentials_manager = SpotifyClientCredentials(client_id = sp_client_id, client_secret = sp_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
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
    
    with open('s3://access_key:secret_key@my_bucket/track_artist_test.json', 'w') as f:
        json.dump(artists_info, f)


def track_pop_upload(bucket_name,s3_file_down,s3_file_up,access_key,secret_key,region,sp_client_id,sp_client_secret):
    session=boto3.Session(aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name=region)
    s3=session.resource('s3')
    bucket=s3.Bucket(bucket_name)
    down_obj=bucket.Object(key=s3_file_down)
    down_content=down_obj.get()['Body'].read().decode()
    json_content=json.loads(down_content)
    #artist_ids=json_content['artist_ids']
    track_ids=json_content['track_ids']
    
    client_credentials_manager = SpotifyClientCredentials(client_id = sp_client_id, client_secret = sp_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    track_pop=[]
    for i in track_ids:
        row={}
        row['track_id']=sp.track(i)['id']
        row['track_popularity']=sp.track(i)['popularity']
        track_pop.append(row)
    
    with open('s3://access_key:secret_key@my_bucket/track_pop_test.json', 'w') as f:
        json.dump(track_pop, f)

def track_audio_upload(bucket_name,s3_file_down,s3_file_up,access_key,secret_key,region,sp_client_id,sp_client_secret):
    session=boto3.Session(aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name=region)
    s3=session.resource('s3')
    bucket=s3.Bucket(bucket_name)
    down_obj=bucket.Object(key=s3_file_down)
    down_content=down_obj.get()['Body'].read().decode()
    json_content=json.loads(down_content)
    #artist_ids=json_content['artist_ids']
    track_ids=json_content['track_ids']
    
    client_credentials_manager = SpotifyClientCredentials(client_id = sp_client_id, client_secret = sp_client_secret)
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
    
    with open('s3://access_key:secret_key@my_bucket/track_audio_test.json', 'w') as f:
        json.dump(features, f)
   
    
t1=PythonOperator(task_id='artist',python_callable=artist_upload,op_kwargs={'bucket_name':'my-bucket','s3_file_down':'artist_track_ids_test.json','s3_file_up':'artists_info_test.json','access_key':'my_access_key','secret_key':'my_secret_key',
                   'region':'us-east-2','sp_client_id':'my_sp_id','sp_client_secret':'my_sp_secret'},dag=dag)
                
t2=PythonOperator(task_id='track_pop',python_callable=track_pop_upload,op_kwargs={'bucket_name':'my-bucket','s3_file_down':'artist_track_ids_test.json','s3_file_up':'track_pop_test.json','access_key':'my_access_key','secret_key':'my_secret',
                   'region':'us-east-2','sp_client_id':'my_sp_id','sp_client_secret':'my_sp_secret'},dag=dag)   
        
t3=PythonOperator(task_id='track_audio',python_callable=track_audio_upload,op_kwargs={'bucket_name':'my_bucket','s3_file_down':'artist_track_ids_test.json','s3_file_up':'track_audio_test.json','access_key':'my_access','secret_key':'my_secret',
                   'region':'us-east-2','sp_client_id':'my_sp_id','sp_client_secret':'my_sp_secret'},dag=dag)


t1 >> t2 >> t3

















