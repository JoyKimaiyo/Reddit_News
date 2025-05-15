## Stay in the know with Reddit’s top trending tech discussions.
Keeping up with the new trends in any technological field is important. Tech changes everyday — you don't want to be passed by the new tools and skills in data.

Reddit helps users stay updated on the latest news and trends. Its forum-style structure facilitates real-time discussions and insights on ongoing events. Reddit fosters a sense of community among its users and has emerged as an indispensable platform for tech enthusiasts looking to stay abreast of the ever-changing technology landscape.

This app offers an opportunity to:

Keep updated with the latest news in the data field
Explore hot topics from leading subreddits
Get AI assistance to understand key concepts and tools

The app updates daily

Link https://joykimaiyo-reddit-news-newsbotnewsbot-khpeeh.streamlit.app/

## To start;
### Clone the repo
git clone https://github.com/JoyKimaiyo/Reddit_News

cd Reddit_News

### Get Reddit_API Credentials

Go to go to https://www.reddit.com/prefs/apps 

Create a new app. named it the way you want 
Tick the script option and redirect url put http://localhost:8080 
create the app 
it will give you client_id under the personal script use and the client_secret (secret) 

create a .env and put the API details also include your reddit username and password.
clne the repository


docker-compose up --build

### Gemini API Credentials

Go to google ai studio
create API key
then add GEM_API to the env too
Also your DB_PASSWORD

Your .env should be like this
REDDIT_CLIENT_ID=client_id
REDDIT_SECRET=secret
REDDIT_APP_NAME=newsbot
REDDIT_USERNAME=ExistingManner4433
REDDIT_PASSWORD=.....

DB_PASSWORD=.....


GEM_API=.....