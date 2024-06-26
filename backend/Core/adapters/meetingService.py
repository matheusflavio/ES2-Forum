import sys

from backend.Core.models.meeting import *
sys.path.insert(0,"..")
import psycopg2
import jwt
from backend.Core.ports.meetingRepo import meetingRepository

class meetingSerivce(meetingRepository):
    def getMeetingTitle(meetingId, conn) -> str:
        cursor = conn.cursor()
        cursor.execute('''SELECT titulo FROM reuniao WHERE id = %s''', (meetingId,))
        meetingTitle = cursor.fetchone()[0]
        if meetingTitle==None:
            return 'Meeting not Found'

        conn.commit()
        return meetingTitle

    def getMeetingInfo(token:str,secretKey:str)->dict:
        conn = psycopg2.connect(host='localhost',
                            database='camara_db',
                            user='admin',
                            password='123456')
        cursor = conn.cursor()
        decoded_token = jwt.decode(
            token, secretKey, algorithms=['HS256'])
        data=[]
     
        cursor.execute("SELECT * FROM reuniao ORDER BY date_added, id")
        data = cursor.fetchall()
        
        return {'data': data}
    
    def createNewMeeting(title:str,date:str,token,secretKey:str) -> Meeting:
        decoded_token = jwt.decode(
            token, secretKey, algorithms=['HS256'])
        # only create meeting if an admin requests it
        if(decoded_token['user_type'] == "Chefia"):
            # create meeting
            meeting = meetingFactory(title=title,date=date)
            return meeting
        else:
            raise PermissionError("Only Chefia role allowed")
    
    def insertDB(meeting: Meeting,conn) -> str:
         
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reuniao (titulo, date_added)'
                        'VALUES (%s, %s) RETURNING id',
                        (meeting.title, meeting.date))
        meeting_id = cursor.fetchone()[0]
        conn.commit()
        return {"id_reuniao": meeting_id}