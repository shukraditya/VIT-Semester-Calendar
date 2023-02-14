from __future__ import print_function
import os.path
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def getTimeClass(slots):
    sl = slots.split("+")
    if sl[0][0] == "L":
        lst = []
        temp = []
        c = 0
        stri = ""
        while c < len(sl):
            temp = sl[c:c + 2]
            stri = temp[0] + "+" + temp[1]
            c += 2
            lst.append(stri)
        sl = lst
    fullLst=[]

    with open("timelist.csv", "r") as file:
        csvr = csv.reader(file)
        for row in csvr:
            fullLst.append(row)

    dic = {"Monday": "2023-02-20", "Tuesday": "2023-02-21", "Wednesday": "2023-02-15", "Thursday": "2023-02-16",
           "Friday": "2023-02-17"}
    ret_lst=[]
    for x in sl:
        for i in fullLst:
            if x == i[0]:
                temp = i[1:]
                for el in temp:
                    if el != "":
                        day = el.split(" ")[0]
                        start_time = el.split(" ")[1].split("-")[0]
                        end_time = el.split(" ")[1].split("-")[1]
                        day_date = dic.get(day)
                        start_time = start_time[0:2] + ":" + start_time[2:] + ":00+05:30"
                        end_time = end_time[0:2] + ":" + end_time[2:] + ":00+05:30"
                        start_dt = day_date + "T" + start_time
                        end_dt = day_date + "T" + end_time
                        ret_lst.append(start_dt)
                        ret_lst.append(end_dt)

    return ret_lst


def class_list_gen():
    f = open("Paru_text.txt", "r")
    x = f.readlines()
    newL = []
    for i in range(2, len(x)):
        if x[i] != "\n":
            newL.append(x[i].strip("\n-"))
    temp = []
    fullLst = []
    for i in range(len(newL)):
        if i % 16 == 2:
            temp.append(newL[i].split(' ')[0])  # Course Code
            temp.append(' '.join(newL[i].split(' ')[2:]))  # Course Name
        elif i % 16 == 8:
            newL[i]=newL[i].strip()
            temp.append(newL[i])  # Slot
        elif i % 16 == 9:
            temp.append(newL[i])  # Venue
        elif i % 16 == 10:
            fac_name = newL[i]  # Faculty Name
        elif i % 16 == 11:
            fac_school = newL[i]  # Faculty School
            temp.append(fac_name + fac_school)
        elif i % 16 == 15:
            fullLst.append(temp)
            temp = []
            fac_name = ""
            fac_school = ""

    return fullLst




def trying():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    class_list = class_list_gen()
    for test_lst in class_list:
        desc = "Course Code : {0} \nCourse Name : {1} \n Slots: {4}\nLocation : {2} \nProfessor : {3}".format(test_lst[0], test_lst[1], test_lst[3], test_lst[4],test_lst[2])
        summary = test_lst[0]+" "+test_lst[1]
        print(desc)
        tC = getTimeClass(test_lst[2])
        c = 0
        while c < len(tC):
            start = tC[c:c + 2][0]
            stop = tC[c:c + 2][1]
            c += 2
            print("Start:",start,"Stop:",stop)
            try:
                service = build('calendar', 'v3', credentials=creds)
                event = {
                    'summary': summary,
                    'location': test_lst[3],
                    'description': desc,
                    'start': {
                        'dateTime': start,
                        'timeZone': 'Asia/Kolkata',
                    },
                    'end': {
                        'dateTime': stop,
                        'timeZone': 'Asia/Kolkata',
                    },
                    'recurrence': [
                        'RRULE:FREQ=WEEKLY;UNTIL=20230617;'
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 20},
                        ],
                    },
                }
                event = service.events().insert(
                    calendarId='6017af51b590b040cd9a0d7c27bd33dcf7c329ab45f070cef6469680a1345225@group.calendar.google.com',
                    body=event).execute()
                print('Event created: %s' % (event.get('htmlLink')))
            except HttpError as error:
                print('An error occurred: %s' % error)



def main():
    trying()


if __name__=="__main__":
    main()


