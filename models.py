"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    wins = ndb.IntegerProperty(required=True, default = 0)

    def to_form(self):
        return UserForm(name=self.name, wins=self.wins,)

class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    game_cancelled = ndb.BooleanProperty(required=True, default=False)
    points = ndb.IntegerProperty(required=True, default=0)
    history = ndb.PickleProperty(required=True, default = [])

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        print Game
        game = Game(user=user,
                    target=Game.rando_select(),
                    )
        game.put()
        print game
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.game_cancelled = self.game_cancelled
        form.points = self.points
        # form.history = self.history
        form.message = message
        return form

    def end_game(self, won):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        # Add the game to the score 'board'
        score = Score.query(Score.user == self.user).get()
        print score
        user = User.query(User.key == self.user).get()
        print user
        if not score:
            score = Score(user=self.user)
        print score
        if won:
            score.won = True
            self.points += 3
            user.wins += 1
        print score
        score.put()
        self.put()
        user.put()

    @classmethod
    def rando_select(self):
         """Returns a randomly selected 'rock','paper','scissors'"""
         rando_select = random.choice(('rock','paper','scissors'))
         return rando_select

    def cancel_game(self):
        """Cancels a game"""
        self.game_cancelled = True
        self.game_over = True
        return

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True,default=date.today())
    won = ndb.BooleanProperty(required=True, default=False)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date))

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    message = messages.StringField(3, required=True)
    user_name = messages.StringField(4, required=True)
    game_cancelled = messages.BooleanField(5, required = True)
    points = messages.IntegerField(6,required=True)
    # history = messages.StringField(7,repeated = True)

class NewGameForm(messages.Message):
    """Used to prompt for a user's name"""
    user_name = messages.StringField(1, required=True)

class GameForms(messages.Message):
    """Returns multiple GameForms"""
    games = messages.MessageField(GameForm, 1, repeated = True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class HistoryMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    history = messages.StringField(1, required=True)

class UserForm(messages.Message):
    """UserForm for outbound User information, excluding email"""
    name = messages.StringField(1,required=True)
    wins = messages.IntegerField(2,required=True)

class UserForms(messages.Message):
    """Return multiple UserForms"""
    users = messages.MessageField(UserForm, 1, repeated=True)

