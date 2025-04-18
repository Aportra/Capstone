from scraping_data.scrape_games import scrape_current_games
from cleaning_data.cleaning_script import clean_current_player_data,clean_current_team_ratings
from outcomes import current_outcome

print("Starting scraping of game data")

team_data,player_data,date = scrape_current_games()

print("Cleaning Data")

# clean_current_player_data(player_data,date)

# clean_current_team_ratings(team_data)

current_outcome(player_data,date)

