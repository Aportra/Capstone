from scraping_data.scrape_games import scrape_current_games,scrape_past_games
from scraping_data.scrape_team_data import scrape_current_team_data
from cleaning_data.cleaning_script import clean_current_player_data
print("Starting scraping of game data")

scrape_past_games()

# data,credentials,length = scrape_current_games()

# print("Cleaning Data")

# clean_current_player_data(data,credentials)

# print("Starting scraping of team data")

# scrape_current_team_data(length) 