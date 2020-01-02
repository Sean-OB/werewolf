from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from urllib.parse import parse_qs
from sms.models import User, SelectedRoles, AvailableRoles
import os

from twilio.twiml.messaging_response import MessagingResponse

# Create your views here.
@csrf_exempt
def receive_sms(request):
    number = parse_qs(request.body)[b'From'][0].decode('utf-8')
    content = parse_qs(request.body)[b'Body'][0].decode('utf-8')

    words = content.split()
    start = words[0].lower()[0]

    # LIST OF VALID COMMANDS AND STARTING CHARACTERS
    update_starts = 'fls'
    admin_commands = ('start', 'restart')

    if start in update_starts:
        # updating something in the database (names, game status, etc)
        with connection.cursor() as cursor:
            print('Database connection opened!')
            if words[0] == 'admin':
                if len(words) == 1:
                    # Get the name of the admin
                    msg_txt = 'The admin is ' + os.environ['ADMIN_NAME']
                elif number != os.environ['ADMIN_NUMBER']:
                    # error message (you aren't the admin!)
                    msg_txt = "You cannot perform admin tasks unless you are the admin. The admin is " + os.environ['ADMIN_NAME'] + '.'
                elif words[1].lower() == 'start':
                    if check_num_rows('sms_selectedroles', cursor) != 0:
                        msg_txt = "A game has already been started!"
                        resp = MessagingResponse()
                        resp.message(msg_txt)
                        return HttpResponse(str(resp))
                    # start the game
                    msg_txt = 'Welcome, ' + os.environ['ADMIN_NAME'] + '. Let\'s get this game started for you.'
                    start_game(cursor)
                elif words[1] == 'restart':
                    msg_txt = "Restarting the game!"
                    end_game(cursor)
                    start_game(cursor)
                elif words[1] == 'end':
                    msg_txt = 'Ending the game!'
                    end_game(cursor)
            elif start == 'f' and len(words) > 1:
                # updating first name
                cursor.execute("""INSERT OR IGNORE INTO sms_user(first_name, last_name, phone_number)
                                 VALUES (%s, NULL, %s);
                             """, (words[1], number))
                cursor.execute("UPDATE sms_user SET first_name=%s WHERE phone_number LIKE %s;",
                            (words[1], number))
                msg_txt = 'Thank you, ' + str(words[1]) + '. Your first name has been updated.'
            elif start == 'l' and len(words) > 1:
                # updating last name
                cursor.execute("""INSERT OR IGNORE INTO sms_user(first_name, last_name, phone_number)
                                VALUES (NULL, %s, %s);
                                """, (words[1], number))
                cursor.execute("UPDATE sms_user SET last_name=%s WHERE phone_number LIKE %s;",
                             (words[1], number))
                msg_txt = 'Thank you. Your last name has been updated.'
            elif ' '.join(words[:1]).lower() == 'get role':
                # give role if game is started, otherwise error
                pass
            else:
                pass
                # unknown command
    elif start == 'h':
        msg_txt = """
        Here are some commands that you can run.\n
        F <first name>:\tUpdate your first name.\n
        L <last name>:\tUpdate your last name.\n
        H:\tAccess these help options.
        """

    resp = MessagingResponse()
    resp.message(msg_txt)

    return HttpResponse(str(resp))

def check_num_rows(table_name, cursor):
    cursor.execute("SELECT count(*) from %s;", (table_name,))
    row = cursor.fetchone()
    return row[0]

def start_game(cursor):
    pass

def end_game(cursor):
    cursor.execute('DELETE FROM sms_availableroles;')


    
