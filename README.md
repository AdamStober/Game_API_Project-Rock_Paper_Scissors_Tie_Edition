#Full Stack Nanodegree Game API Project:
#Rock, Paper, Scissors - Tie Edition

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Rock, paper, scissors tie edition is a game of chance. Each game begins with a random 'target'
among the three: 'rock', 'paper', or 'scissors'.  Rock beats scissors, scissors beats
paper, and paper beats rock.  A tie results in a point, and the game continues
until the player wins or loses.  A win is worth 3 additional points, and counts as a win in
the standings.

##How to Play
After the player has created a user (once ever) and a game (each game), the player makes moves:
Each 'guess' is sent to the `make_move` endpoint which will reply
with what is entered, what the opponent had, and whether the move resulted in a tie,
a win, or a loss.

Many different Rock, Paper, Scissors tie edition games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess', records that guess into a history log, and
    returns the updated state of the game.  If the guess matches the target, a new
    target is generated.  If a game results in a win, a Score entity will be updated.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: GameForms.
    - Description: Returns all Scores in the database (unordered).
    
- **get_high_scores**
    - Path: 'scores/leaderboard'
    - Method: GET
    - Parameters: None
    - Returns: GameForms.
    - Description: View a list of high scores in descending order

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms. 
    - Description: Returns all Scores ("points") recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_games**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms
    - Description: Returns active games for the specified User.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm
    - Description: Cancels a game in progress.

- **get_user_rankings**
    - Path: 'user/rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: View a ranking of users with the most wins, regardless of points

- **get_game_history**
    - Path: 'game/{urlsafe_game_key}/game_history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: HistoryMessage
    - Description: View a summary of a game's guesses and targets.

##Models Included:
 - **User**
    - Stores unique user_name, number of wins, and (optional) email address.
    
 - **Game**
    - Stores unique game states including points. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with User model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state
    - urlsafe_key, game_over, message, user_name, game_cancelled, points
 - **GameForms**
    - Multiple GameForm container
 - **NewGameForm**
    - Used to create a new game
    - user_name
 - **MakeMoveForm**
    - Inbound make move form
    - guess
 - **ScoreForm**
    - Representation of a completed game's Score
    - user_name, date, won
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **HistoryMessage**
    - General purpose String container.
- **UserForm**
    - Representation of a User's standing
    - user_name, wins
    - (optional) email field intentionally omitted for security reasons
 - **UserForms**
    - Multiple UserForm container.

### Special Thanks
Udacity Andy Brown, Disqus Kash "money" Malik, Nik
