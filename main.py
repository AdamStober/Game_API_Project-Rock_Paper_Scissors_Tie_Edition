#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging
import webapp2
from google.appengine.api import mail, app_identity
from api import RockPaperScissorsTieEdition
from models import User, Game

class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every 48 hours using a cron job"""
        app_id = app_identity.get_application_id()
        # Get users with email addresses.
        users = User.query(User.email != None)
        for user in users:
            # Get users active games.
            games = Game.query(Game.user == user.key, Game.game_over == False).fetch()
            if games:
                # Send the user a reminder.
                subject = 'Finish what you started!'
                body = 'Hello {}, you have active games. Come play Rock, Paper Scissors Tie Edition!'.format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)