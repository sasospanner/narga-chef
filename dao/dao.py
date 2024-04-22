import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg
import dao.guilds
import dao.members
import dao.options
import dao.requests

load_dotenv()

HOST = os.environ.get("host")
PASSWORD = os.environ.get("password")
DB_USER = os.environ.get("db_user")
DB_NAME = "narga"

# connection = psycopg.connect(f"dbname=narga user=narga host={HOST} password={PASSWORD}")

def setup(guild_id: int, guild_name: int, currency: str, submission_channel: int, review_channel: int, info_channel: int, cooldown: int):
    #Reconnecting everytime because else the connect object will go out of scope
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection: 
        with connection.cursor() as cursor:
            res = dao.guilds.select(cursor, guild_id)
            if(res != None):
                dao.guilds.update(cursor, guild_id, guild_name, currency, submission_channel, review_channel, info_channel, cooldown)
            else:
                dao.guilds.insert(cursor, guild_id, guild_name, currency, submission_channel, review_channel, info_channel, None, cooldown)

def refreshAndGetMember(cursor, guild_id, member_id, nickname):
    res = dao.members.select(cursor, guild_id, member_id)
    if(res == None):
        dao.members.insert(cursor, guild_id, member_id, nickname, 0, datetime.min, None)
        res = dao.members.select(cursor, guild_id, member_id)
    else: #Update nickname for database maintenability
        dao.members.update(cursor, res[0], res[1], nickname, res[3], res[4], res[5])
    return res

def getGuild(guild_id: int):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.guilds.select(cursor, guild_id)

def getRank(guild_id: int, member_id: int):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.members.rank(cursor, guild_id, member_id)

def getMember(guild_id: int, member_id: int, nickname: str):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return refreshAndGetMember(cursor, guild_id, member_id, nickname)

def update_member_submission(guild_id: int, member_id: int, last_submission: str):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.members.update_submission(cursor, guild_id, member_id, datetime.utcnow(), last_submission)

def requestRegister(guild_id, request_type, name, effect, value):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.requests.insert(cursor, guild_id, request_type, name, effect, value)

def requestDelete(guild_id, request_type, name, effect):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.requests.delete(cursor, request_type, guild_id, name, effect)

def getRequest(guild_id, request_type, name, effect):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.requests.selectOne(cursor, guild_id, request_type, name, effect)

def requests(guild_id, request_type = None, name = None, effect = None):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.requests.select(cursor, guild_id, request_type = request_type, request_name = name, effect = effect)

def add_points(guild_id, member_id, points):
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} host={HOST} password={PASSWORD}") as connection:
        with connection.cursor() as cursor:
            return dao.members.add_points(cursor, guild_id, member_id, points)

# Groups every column in lists 
def requestPerColumn(guid_id, request_type = None, name = None, effect = None):
    db_res = requests(guid_id, request_type, name, effect)
    request_type = []
    name = []
    effect = []
    value = []
    for row in db_res:
        request_type.append(row[1])
        name.append(row[2])
        effect.append(row[3])
        value.append(row[4])
    request_type = list(dict.fromkeys(request_type))
    name = list(dict.fromkeys(name))
    effect = list(dict.fromkeys(effect))
    value = list(dict.fromkeys(value))
    return {"type":request_type, "name": name, "effect": effect, "value": value}
