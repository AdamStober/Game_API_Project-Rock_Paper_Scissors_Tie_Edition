# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms,GameForms,HistoryMessage,UserForm,UserForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),email=messages.StringField(2))
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(GameForms)

#*# re-write to "guess rock, paper, scissors"
@endpoints.api(name='rock_paper_scissors_tie_edition', version='v1')
class RockPaperScissorsTieEdition(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('Something went wrong!')
        return game.to_form('Good luck playing rock, paper, scissors -- tie edition!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Rock, paper, scissors: What a fun game!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # print game
        # if not game:
        #   raise endpoints.NotFoundException(
        #             'That game does not exist! Go make a new one!')
        if game.game_over:
            print game
            return game.to_form('Game already over!')
        #game.history.append(['Guess: '+str(request.guess),'Target: '+str(game.target)])
        #game.history.append({'message':request.guess,'guess':game.target})
        game.history.append({'player_move':request.guess,'computer_move':game.target})
        #game.history.append(('Guess: ':request.guess,'Target: ':game.target))
        if request.guess == game.target:
          game.points += 1
          msg = '%s vs %s! Tie! Take a point and try again!' % (request.guess , game.target)
        elif request.guess == 'rock':
          if game.target == 'paper':
            game.end_game(False)
            return game.to_form('You lose! Paper beats rock')
          else:
            game.end_game(True)
            return game.to_form('You win! rock beats scissors!')
        elif request.guess == 'paper':
          if game.target == 'scissors':
            game.end_game(False)
            return game.to_form('You lose! Scissors beats paper')
          else:
            game.end_game(True)
            return game.to_form('You win! Paper beats rock!')
        elif request.guess == 'scissors':
          if game.target == 'rock':
            game.end_game(False)
            return game.to_form('You lose! Rock beats scissors')
          else:
            game.end_game(True)
            return game.to_form('You win! Paper beats rock!')
        else:
          msg = 'That\'s not a valid play. Try rock, paper, or scissors.'
        # re-set computer to random rock, paper, or scissors
        game.target = Game.rando_select()
        print game
        game.put()
        return game.to_form(msg)

    @endpoints.method(response_message=GameForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return GameForms(games=[game.to_form('Look at those points!') for game in Game.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.user == user.key)
        return GameForms(games=[game.to_form("nice!") for game in games])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.game_over == False, Game.user == user.key)
        return GameForms(games=[game.to_form("Active game! Go play!") for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game in progress. Users are not permitted to remove completed games."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        print game
        if game.game_over == True:
            raise endpoints.BadRequestException('Completed games cannot be cancelled, you dodo!')
        if game.game_cancelled == True:
            raise endpoints.BadRequestException('Game has already been cancelled, you dodo!')
        game.cancel_game()
        game.put()
        return game.to_form('Game has been cancelled')

    @endpoints.method(response_message=GameForms,
                      path='scores/leaderboard',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """View a list of high scores in descending order"""
        high_scores = Game.query(Game.points>0).order(-Game.points)
        return GameForms(games=[game.to_form('Great score!') for game in high_scores])

    @endpoints.method(response_message=UserForms,
              path='user/rankings',
              name='get_user_rankings',
              http_method='GET')
    def get_user_rankings(self, request):
        """View a ranking of users with the most wins, regardless of points per game"""
        wins = User.query().order(-User.wins)
        return UserForms(users=[win.to_form() for win in wins])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryMessage,
                      path='game/{urlsafe_game_key}/game_history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns a summary of a game's guesses and targets."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return HistoryMessage(history=str(game.history))

api = endpoints.api_server([RockPaperScissorsTieEdition])
