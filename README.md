# Spotify-Top-200-Dashboard-Project

## Background

Music is my life saver, when I am happy, sad, or just being bored, I’m used to put on my earphone and sink into my music world. Spotify is a good assistant to let me find my favorite songs and as a data analyst, I’m also very interested in playing with the data that Spotify provided via its website and API.

In this project, I scraped Spotify Top200 Charts for all the 65 countries(exclude ‘global’ to avoid overlap) in July 2020 and also extracted these tracks' popularity, audio features and related artists information and created a dashboard with Tableau to show the weekly stream trend, most popular tracks and most active artists in July. And specifically, with the audio feature: energy, I visualize the countries whose top 200 tracks are most energetic.

## Installation

In this project, I have used Spotipy, a well-known package to play with Sotify API, related documents can be found here:
[Spotipy documentation](https://spotipy.readthedocs.io/en/2.13.0/)

`pip install spotipy`

I used Apache Airflow to automate the ETL process. Airflow is an open-source workflow management platform, related documents can be found here:
[Apache Airflow documentation](https://airflow.apache.org/docs/stable/)

`pip install apache-airflow`

And I also used Beatifule Soup to scrape web data, and used smart_open and boto3 to read and write data to AWS s3 bucket.

`pip install beautifulsoup4`

`pip install smart_open`

`pip install boto3`

## ETL

I wrote two classes, one for getting the necessary parameters for data extraction, and the other one for all methods that extracting needed data.
The class can be find here: [Spotify Top 200 class]

As the time needed to extract all the needed data is very long (52000 records of top 200 tracks in 65 countries and all tracks popularity, audio feature and artists information), I created an Airflow dag to run the ETL process automatically. The dag can be find here.

The ETL process is like below:



## Dashboard

I used Tableau to connect all the four tables: Top 200 charts, Track popularity, Track Audio Features and Track Artists and joint them together by track_id. 

Hereunder is the demonstrate of the dashboard I made:


From this dashboard, I found the difference of weekly stream in all the four weeks of July is very subtle, and in this month, the most energetic country is Japan while the most peaceful one is Indonesia. 

I also found there is an obvious connection between track stream and track popularity.

For each artist, I defined the most active artist as who has the greatest number of streams in July. I found the most active artists are the ones that have very high popularity and have released new songs or album just before July or in July. But there are no direct connection between artists stream and the number of distinct tracks that listed in top 200 charts.

In this dashboard, all of the four charts are interactive with each other. 

For example, by clicking each artist, I can check his or her weekly stream, most popular track and even the energy index for the tracks in different country.

To sum up, I think the spotify API provided lots of interesting data to play with, for example, other than creating dashboard, people also can build machine learning model for track 

