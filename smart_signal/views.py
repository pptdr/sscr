import os, csv
#import petl as etl
from typing import Dict, Any
from datetime import datetime
import time
import pandas as pd
from django.db.models import Count,Max
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Client,signal_details
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth import views as auth_views
from django import forms
from django.views.generic import FormView

def trail_of_db(request):
    insert_to_signal_details_db("s1","sangli-gavbhag","2020-10-10",4,"hello.mp4",10,10)
    return render(request,"layout1.html")

def insert_to_signal_details_db(cnm, signal_loc, created_dt,created_time, size_of_vid, vid_tit, freq, sub_period):
        object1 = signal_details()
#        print("videotit dt size fre per:", vid_tit, created_dt, size_of_vid, freq, sub_period)
        object1.cnm = cnm
        object1.signal_name = signal_loc
        #    object1.video_title = vid_tit
        t1 = vid_tit
        t2 = created_dt
        t3 = created_time
        t4 = size_of_vid
        object1.created_on = created_dt
        object1.created_at_time = created_time
        object1.size_of_video = size_of_vid
        object1.video_title = vid_tit
        object1.frequency = freq
        object1.subscription_period = sub_period

        object1.save()
        print("Object saved: ", object1)

def about(request):
    return render(request, 'about.html')

def layout(request):
   # return render(request, 'layout.html')
     return render(request,'layout1.html')

def home(request):
    if request.user.is_superuser:
        return render(request, 'adminpage.html')
    else:
        return render(request,'userpage.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        unm = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=unm, password=password)

        if user is not None:
            auth.login(request, user)
            if request.user.is_superuser:
                return render(request, 'adminpage.html')
            else:
                return render(request, 'userpage.html')
        else:
            messages.info(request, "Invalid credentials")
            return redirect('layout1')
    else:
        return render(request, 'layout1.html')

def adminpage(request):
    return render(request, 'adminpage.html')

def userpage(request):
    return render(request, 'userpage.html')


def get_companyname(current_user):
    company_name = ''
    clidetails = Client.objects.all()

    for client in clidetails:
        client_user = str(client.user)

        if current_user == client_user:
           # print('current_user's company name: ', client.company_name)
            company_name = client.company_name

    return company_name

def get_city_and_location(current_user):
    values = {}
    company_name = get_companyname(current_user)
 #   print('company name in get_city_and_location: ',company_name)
    values["company_name"] = company_name

    cmd = 'aws s3 ls s3://ecube-eis/' + str(company_name) + '/'
    cmd1 = cmd + ' > city.txt'
  #  print(cmd1)
    res = os.popen(cmd1)
    res1 = res.read()

    df = pd.read_csv("city.txt", delimiter=',')
    df.to_csv('city1.csv')
    f = open("city1.csv", "r")
    reader1 = csv.reader(f)
    reader = list(reader1)
   # print("reader: ", reader)
    num_rows = len(reader) -1
    city_names = []
    for line in range(num_rows):
        #print('col:', row[1])
        row = reader[line]
        val = 'PRE' in row[1]
        t3 = ''
        if val:
            t3 = row[1].replace('PRE', ' ')

        t4 = t3.strip()
        backslash = '/'
        val = backslash in t4
        t3 = ''
        if val:
            t3 = t4.replace(backslash, ' ')

        t4 = t3.strip()
        city_names.append(t4)

    values["city_names"]=city_names
    #print('value',values)

    return values

def time_conversion(temp_date,temp_time):
    totalSecs = 0
    gmt_format = '5:30:00'
    timeList = []
    timeList.append(temp_time)
    timeList.append(gmt_format)
    for tm in timeList:
        timeParts = [int(s) for s in tm.split(':')]
        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
    totalSecs, sec = divmod(totalSecs, 60)
    hr, min = divmod(totalSecs, 60)
    final_date = temp_date
    temp_hr = hr

    strzero = '0'
    if hr >= 24:
        hr = temp_hr - 24
        dateparts = [int(s) for s in temp_date.split('-')]
        new_date = dateparts[2] + 1

        if dateparts[1] < 10:
            month = strzero + str(dateparts[1])
        else:
            month = str(dateparts[1])

        final_date = str(dateparts[0])+"-"+month+"-"+str(new_date)

    #print(final_date)
    #print("%d:%02d:%02d" % (hr, min, sec))
    str_time = str(hr)+":"+str(min)

    return str_time,final_date

def get_videos(res1, cnm , location):
    #print('res1 in get_videos:', res1)
    #print('cnm and location in get_videos: ',cnm,location)

    num_rows = len(res1) - 1
    a = [[0] * 5 for i in range(num_rows)]
    # a[0][0], a[0][1], a[0][2], a[0][3] = "Date", "Time", "Size in KB", "Video"
    for j in range(num_rows):
        a[j][0] = j + 1
        a[j][1], a[j][2], a[j][3], a[j][4] = res1[j + 1].split()
        MBFACTOR = float(1 << 20); 
        mb= int(a[j][3]) / MBFACTOR
       #print("video size in mb: ",mb)
        temp = a[j][4]
        t1 = cnm + '/' + location + '/'
        val = t1 in temp
        t = ''
        tt,dt = time_conversion(a[j][1],a[j][2])
     #   print(tt)
        a[j][1] = dt
        a[j][2] = tt
        a[j][3] = round(mb)
        if val:
            t = temp.replace(t1, ' ')
        a[j][4] = t

    return a

def get_clientlist():
    clients_list = []
    clidetails = Client.objects.all()
    count = 0
    temp = []
    for c in clidetails:
        count = count + 1
        temp.append(c.company_name)

    temp.sort()
    num_rows = count
    #print('num_rows: ', num_rows)
    clients_list = [[0] * 2 for i in range(num_rows)]
    for j in range(num_rows):
        clients_list[j][0] = j + 1
        clients_list[j][1] = str(temp[j])

    #print("Clients_list in get_clientlist: ",clients_list)
    return clients_list

def get_signals():
    clidetails = Client.objects.all()
    city_list= {}
    city_names = []
    i = 0
    sorted_cnm_list =[]
    for client in clidetails:
        client_user = str(client.user)
        company_name = get_companyname(client_user)
        sorted_cnm_list.append(company_name)

    sorted_cnm_list.sort()
    #print("sorted cnm list: ",sorted_cnm_list)
    temp1= ''
    for cnm in sorted_cnm_list:
        for client in clidetails:
            client_user = str(client.user)
            company_name = get_companyname(client_user)
            if cnm == company_name:
                temp1 = client_user
                break

     #   print(temp1)
        city = get_city_and_location(temp1)
        city_list.update({city["company_name"]: city["city_names"]})

    #print('city_list:',city_list)

    return city_list


def get_all_clients_and_signals():
    clidetails = Client.objects.all()
    full_list = []
    for client in clidetails:
        current_user = str(client.user)
        company_name = get_companyname(current_user)
        # print('company name in get_all_clients_and_signals: ',company_name)

        cmd = 'aws s3 ls s3://ecube-eis/' + str(company_name) + '/'
        cmd1 = cmd + ' > city.txt'
     #   print(cmd1)
        res = os.popen(cmd1)
        res1 = res.read()
     #   print('res1 :', res1)
        df = pd.read_csv("city.txt", delimiter=',')
        df.to_csv('city1.csv')
        f = open("city1.csv", "r")
        reader1 = csv.reader(f)
        reader = list(reader1)
      #  print("reader: ", reader)
        num_rows = len(reader) - 1
        city_names = []
        for line in range(num_rows):
            # print('col:', row[1])
            row = reader[line]
            val = 'PRE' in row[1]
            t3 = ''
            if val:
                t3 = row[1].replace('PRE', ' ')

            t4 = t3.strip()
            backslash = '/'
            val = backslash in t4
            t3 = ''
            if val:
                t3 = t4.replace(backslash, ' ')

            t4 = t3.strip()
            t5 = company_name + '/' + t4
            city_names.append(t5)
            full_list.append(t5)

    full_list.sort()
    #print(full_list)
    return full_list

def show_signals(request):
    city_list = get_signals()
    return render(request, 'show_signals.html',{'city_list':city_list, 'dict_len':len(city_list)})

def addclient(request):
    if request.method == 'POST' and 'create_user' in request.POST:
            cnm = request.POST['company_name']
            clogo = request.POST['company_logo']
            fnm = request.POST['first_name']
            lnm = request.POST['last_name']
            unm = request.POST['username']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                if User.objects.filter(username=unm).exists():
                    messages.info(request, 'Username is taken')
                    return redirect('addclient')
                elif User.objects.filter(email=email).exists():
                    messages.info(request, 'Email is taken')
                    return redirect('addclient')
                else:
                    user = User.objects.create_user(username=unm, password=password1, email=email, first_name=fnm,
                                                last_name=lnm)

                client1 = Client()
                client1.user = user
                client1.company_name = cnm
                client1.company_logo = clogo
                user.save()
                client1.save()
                messages.info(request, 'New User created')
                clients_list = get_clientlist()

                cmd = ''
                return render(request, 'show_clients.html', {'client_list': clients_list})
            else:
                messages.info(request, 'Password not matching')
                return redirect('addclient')
    else:
        #print("in else part")
        return render(request,'addclient.html')

    return render(request, 'client_menu.html')

def client_menu(request):
    return render(request, 'client_menu.html')

def show_clients(request):
    clients_list = get_clientlist()
    #print("clients_list in show_clients: ",clients_list)
    return render(request, 'show_clients.html', {'client_list': clients_list})

def deleteclient(request):
    if request.method == 'POST':
        temp = str(request.POST.get('Delete_now'))
        #print('client to delete:',temp)
        temp1 = Client.objects.filter(company_name = temp).delete()
        #print('client deleted')
        clients_list = get_clientlist()
        return render(request, 'show_clients.html', {'client_list': clients_list})
    return render(request, 'addclient.html')

def validate_subscription(current_user,):
    values = get_city_and_location(request.user.username)
    cnm = values['company_name']
    #print('cnm:', cnm)
    city_names = values['city_names']


def create_video_table(fnm,res1,cnm,location,vid_title,frequency,expiry_period):
    #print('res1 in get_videos:', res1)
    #print('cnm and location in get_videos: ',cnm,location)
    with open(fnm, "r") as f:
        reader = csv.reader(f, delimiter=",")
        data = list(reader)
        row_count = len(data)

    num_rows = row_count
    a = [[0] * 7 for i in range(num_rows)]

    reader = csv.reader(fnm, delimiter=',')
    #for row in reader:
    #    (Id, title) = row[0:1]

    for j in range(num_rows):
        a[j][0] = j + 1
        a[j][1], a[j][2], a[j][3], a[j][4],a[j][5],a[j][6],a[j][7] = res1[j + 1].split()
        MBFACTOR = float(1 << 20);
        mb= int(a[j][3]) / MBFACTOR
       #print("video size in mb: ",mb)
        temp = a[j][4]
        t1 = cnm + '/' + location + '/'
        val = t1 in temp
        t = ''
        tt,dt = time_conversion(a[j][1],a[j][2])
#        print(tt)

        a[j][1] = dt
        a[j][2] = tt
        a[j][3] = round(mb)
        if val:
            t = temp.replace(t1, ' ')
        a[j][4] = t
        t = t.strip()
        if t == vid_title:
      #      print("t and video_title: ",t,vid_title)
            a[j][5] = frequency
            a[j][6] = expiry_period
#(cnm, signal_loc, created_dt, size_of_vid, vid_tit, freq, sub_period):
        #insert_to_signal_details_db(cnm,location,a[j][1],a[j][3],vid_title,frequency,expiry_period)
       # print("a in create_video_table:",a)
    return a

def create_video_table_1(fnm):
    #print('res1 in get_videos:', res1)
    #print('cnm and location in get_videos: ',cnm,location)
    with open(fnm, "r") as f:
        reader = csv.reader(f, delimiter=",")
        data = list(reader)
        row_count = len(data)

    num_rows = row_count - 1
    a = [[0] * 7 for i in range(num_rows)]

    f = open(fnm, "r")
    print("filename and row_count ;",fnm,num_rows)
    df = pd.read_csv(f)

    arr_cnm,arr_loc,arr_date,arr_time,arr_size,arr_video,arr_fre,arr_subsc = [],[],[],[],[],[],[],[]
    csv_reader = csv.reader(open(fnm))
    for line in csv_reader:
        arr_cnm.append(line[0])
        arr_loc.append(line[1])
        arr_date.append(line[2])
        arr_time.append(line[3])
        arr_size.append(line[4])
        arr_video.append(line[5])
        arr_fre.append(line[6])
        arr_subsc.append(line[7])

    for j in range(num_rows):
        k = j + 1
        a[j][0] = k
        a[j][1] = arr_date[k]
        a[j][2] = arr_time[k]
        a[j][3] = arr_size[k]
        a[j][4] = arr_video[k]
        a[j][5] = arr_fre[k]
        a[j][6] = arr_subsc[k]

    print("a in create_video_table:",a)
    return a

def add_data_to_file(current_user, location, video_title,frequency,expiry_period):
    cnm = get_companyname(current_user)
    folder_path="/home/ubuntu/ecubesolutions.in/venv/smart_signal/Signal_detail_files/"
#    fnm = folder_path + str(location) + '.txt'
    fnm = str(location) + ".txt"
    file = open(fnm,"a")

    temp_str = [current_user,location,video_title,frequency,expiry_period]
    for temp in temp_str:
        file.writelines(str(temp))
        file.writelines(" ")

    file.writelines("\n")
    file.close()

    return file

def get_date_of_upload(cnm,location,res1,video_title):
    # print('res1 in get_videos:', res1)
    # print('cnm and location in get_videos: ',cnm,location)
    dt_and_size = []
    num_rows = len(res1) - 1
    a = [[0] * 5 for i in range(num_rows)]
    # a[0][0], a[0][1], a[0][2], a[0][3] = "Date", "Time", "Size in KB", "Video"
    for j in range(num_rows):
        a[j][0] = j + 1
        a[j][1], a[j][2], a[j][3], a[j][4] = res1[j + 1].split()
        MBFACTOR = float(1 << 20);
        mb = int(a[j][3]) / MBFACTOR
        # print("video size in mb: ",mb)
        temp = a[j][4]
        t1 = cnm + '/' + location + '/'
        val = t1 in temp
        t = ''
        tt, dt = time_conversion(a[j][1], a[j][2])
      #  print(tt)
        a[j][1] = dt
        a[j][2] = tt
        a[j][3] = round(mb)
        if val:
            t = temp.replace(t1, ' ')
        a[j][4] = t
       # print("t and video_title: ",t,video_title)
        t = t.strip()
        if t == video_title:
        #    print("both are same")
            dt_and_size.append(a[j][1])
            dt_and_size.append(a[j][2])
            dt_and_size.append(a[j][3])
         #   print("Date and size:",dt_and_size)
            break
        else:
            print("in else part")

    return dt_and_size


def remove_duplicated_records(model, fields):
    """
    Removes records from `model` duplicated on `fields`
    while leaving the most recent one (biggest `id`).
    """
    duplicates = model.objects.values(*fields)
    print("duplicates in function: ",duplicates)
    # override any model specific ordering (for `.annotate()`)
    duplicates = duplicates.order_by()

    # group by same values of `fields`; count how many rows are the same
    duplicates = duplicates.annotate(
        max_id=models.Max("id"), count_id=models.Count("id")
    )

    # leave out only the ones which are actually duplicated
    duplicates = duplicates.filter(count_id__gt=1)
    print("duplicates after filtering: ", duplicates)
    for duplicate in duplicates:
        to_delete = model.objects.filter(**{x: duplicate[x] for x in fields})

        # leave out the latest duplicated record
        # you can use `Min` if you wish to leave out the first record
        to_delete = to_delete.exclude(id=duplicate["max_id"])

        to_delete.delete()

    print("duplicates after deleting: ",duplicates)

def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

@csrf_exempt
def new_uploadvideo(request):
    # Copy local file to bucket
    # aws s3 cp file-name s3://bucket-name
    str1 = 'aws s3 cp '

    city_names = []
    vid_len = [10,20,30,40]
    if request.user.is_superuser:
        user_or_admin = 'admin'
        full_list = get_all_clients_and_signals()
    else:
        user_or_admin = 'user'
        values = get_city_and_location(request.user.username)
        cnm = values['company_name']
        #print('cnm:', cnm)
        city_names = values['city_names']
        #if request.method == 'POST' and request.FILES['fileToUpload']:

    if request.method == 'POST':
        #print("\n#### Upload video to given bucket ####\n")
            temp = 's3://ecube-eis/'
            video_length = str(request.POST.get('video_length'))
          #  print("video_length:",video_length)
            if request.user.is_superuser:
                signal_location = str(request.POST.get('company_name'))
            #print(signal_location)
                temp1 = temp + signal_location + '/'
                cnm, location = signal_location.split('/')
            else:
                location = str(request.POST.get('signal'))
                #print(location)
                temp1 = temp + cnm + '/' + location + '/'
	        #print('temp1: ', temp1)

            frequency = str(request.POST.get('freq'))
#            priority =  str(request.POST.get('priority'))
            expiry_period = str(request.POST.get('expiry_date'))
           # print(" freq expiry date:", frequency,expiry_period)

            myfile = request.FILES['fileToUpload']
            fs = FileSystemStorage()
            video_title = str(myfile.name).replace(" ","-")
            filename = fs.save(video_title, myfile)
            #print(myfile.name)
            #print('filesystem: ',filename)
            uploaded_file_url = fs.url(filename)
            path = os.getcwd()
            #print(uploaded_file_url)
            source = str(myfile)
            cmd = str1 + path + uploaded_file_url + ' ' + temp1 + video_length +"-seconds/" + video_title
            #print(cmd)
            res = os.popen(cmd)
            res1 = res.read()
            #insert_to_signal_details_db(cnm,location,"2020-10-20",'2',video_title,frequency,expiry_period)
            #text_file = add_data_to_file(cnm,location,video_title,frequency,expiry_period)

            cmd1 = 'aws s3 ls '
            list_bucket = cmd1 + temp1 + ' ' + '--recursive'
            #print(list_bucket)
            res = os.popen(list_bucket)
            res1 = list(res)
            #print("res1: ",res1)
            temp_str = video_length +"-seconds/" + video_title
            dt = get_date_of_upload(cnm,location,res1,temp_str)
            information =  {'cnm':cnm,'location':location,'created_on':dt[0],'created_at_time':dt[1],'size_of_video':dt[2],'Video_title':temp_str,'frequency':frequency,'expiry_period':expiry_period}
            print("information:",information)
            csv_columns = ['Cnm', 'Location', 'Created_on','Created_at_time','Size_of_video','Video_title','Frequency','Subscription_time']
            filename = location + ".csv"
            filename_processed = location + "_processed.csv"
            csv_file = filename
            #with open(filename,"r") as temp_nm:
            #df1 = pd.read_csv(filename)
            #print("Number of rows ", len(df1.index))

            print("size of file: ",is_non_zero_file(filename))
            if not(is_non_zero_file(filename)):
                try:
                    with open(csv_file, 'a') as csvfile:
                        writer = csv.DictWriter(csvfile, information.keys())
                        writer.writeheader()
                        writer.writerow(information)
                except IOError:
                    print("I/O error")
            else:
                try:
                    with open(csv_file, 'a') as csvfile:
                        writer = csv.DictWriter(csvfile, information.keys())
                        #writer.writeheader()
                        writer.writerow(information)
                except IOError:
                    print("I/O error")

            d = pd.read_csv(filename, keep_default_na=False)
            d.drop_duplicates(subset=['Video_title'], inplace=True, keep='last')
            d.to_csv(filename_processed, index=False)

            #insert_to_signal_details_db(cnm,location,dt[0],dt[1],dt[2],temp_str,frequency,expiry_period)
#            a = get_videos(res1,cnm , location)
#            new_file = check_duplicates_in_file(text_file.name)
#            new_text_file = new_file
            #file_name = "signal_details_processed.csv"
            a = create_video_table_1(filename_processed)

            upload_csv_to_s3 = "aws s3 cp " + filename_processed + " " + "s3://all-signal-text-files"
            print(upload_csv_to_s3)
            tp = os.popen(upload_csv_to_s3)

            return render(request, 'listout_videos.html', {'show_table': a, 'cnm': cnm, 'city': location})
    else:
    #print("in else")
        if user_or_admin == 'admin':
            return render(request, 'new_uploadvideo.html', {'full_list': full_list,'vid_len':vid_len})
        else:
            return render(request, 'new_uploadvideo.html', {'company_name': cnm, 'city_names': city_names,'vid_len':vid_len})

        return render(request, 'new_uploadvideo.html', {'full_list': full_list,'vid_len':vid_len})
    return render(request,'home.html')


@csrf_exempt
def uploadvideo(request):
    # Copy local file to bucket
    # aws s3 cp file-name s3://bucket-name
    str1 = 'aws s3 cp '

    city_names = []
    if request.user.is_superuser:
        user_or_admin = 'admin'
        full_list = get_all_clients_and_signals()
    else:
        user_or_admin = 'user'
        values = get_city_and_location(request.user.username)
        cnm = values['company_name']
        #print('cnm:', cnm)
        city_names = values['city_names']

    #if request.method == 'POST' and request.FILES['fileToUpload']:
    if request.method == 'POST':
        #print("\n#### Upload video to given bucket ####\n")
        temp = 's3://ecube-eis/'
        if request.user.is_superuser:
            signal_location = str(request.POST.get('company_name'))
            #print(signal_location)
            temp1 = temp + signal_location + '/'
            cnm, location = signal_location.split('/')
        else:
            location = str(request.POST.get('signal'))
            #print(location)
            temp1 = temp + cnm + '/' + location + '/'

        #print('temp1: ', temp1)

        myfile = request.FILES['fileToUpload']
        fs = FileSystemStorage()
        video_title = str(myfile.name).replace(" ","-")
        filename = fs.save(video_title, myfile)
        #print(myfile.name)
        #print('filesystem: ',filename)
        uploaded_file_url = fs.url(filename)
        path = os.getcwd()
        #print(uploaded_file_url)
        source = str(myfile)
        cmd = str1 + path + uploaded_file_url + ' ' + temp1 + video_title
        #print(cmd)
        res = os.popen(cmd)
        res1 = res.read()

        cmd1 = 'aws s3 ls '
        list_bucket = cmd1 + temp1 + ' ' + '--recursive'
        #print(list_bucket)
        res = os.popen(list_bucket)
        res1 = list(res)
        a = get_videos(res1,cnm , location)

        return render(request, 'listout_videos.html', {'show_table': a, 'cnm': cnm, 'city': location})
    else:
        #print("in else")
        if user_or_admin == 'admin':
            return render(request, 'uploadvideo1.html', {'full_list': full_list})
        else:
            return render(request, 'uploadvideo1.html', {'company_name': cnm, 'city_names': city_names})

        return render(request, 'uploadvideo1.html', {'full_list': full_list})

    return render(request,'home.html')

@csrf_exempt
def uploadvideo_at_all_sites(request):
    str1 = "aws s3 cp "
    city_names = []
    values = get_city_and_location(request.user.username)
    cnm = values['company_name']
    #print('cnm:', cnm)
    city_names = values['city_names']
    #print("city names: ",city_names)
    if request.method == 'POST':
        #print("\n#### Upload video to given bucket ####..........\n")
        temp = 's3://ecube-eis/' + cnm + '/'
        length = len(city_names)
        myfile = request.FILES['fileToUpload']
        fs = FileSystemStorage()
        video_title = str(myfile.name).replace(" ","-")
        #print("video-title:",video_title)
#        filename = fs.save(myfile.name, myfile)
        filename = fs.save(video_title,myfile)
        #print(myfile.name)
        #print('filename: ', filename)
        uploaded_file_url = fs.url(filename)

        for i in range(length):
            str2 = city_names[i]
            #print("str2: ",str2)
            temp1 = temp + str2 + '/'
            #print('temp: ', temp1)

            path = os.getcwd()
            #print("uploaded file url:",uploaded_file_url)
            source = str(myfile)
            cmd = str1 + path + uploaded_file_url + ' ' + temp1 + video_title
            #print(cmd)
            res = os.popen(cmd)
            res1 = res.read()

        return render(request,'userpage.html')
    else:
        return render(request,'uploadvideo_at_all_sites.html')

@csrf_exempt
def deletevideo(request):
    str1 = 'aws s3 rm s3://ecube-eis/'
#    print("In delete video function")
    if request.method == 'POST':
        if request.user.is_superuser:
            #print("its admin")
            cnm = str(request.POST.get('cnm'))
            city = str(request.POST.get('city_nm'))
            cnm_and_city = cnm + '/' + city + '/'
        else:
            cnm = str(request.POST.get('cnm'))
            city = str(request.POST.get('city_nm'))
            cnm_and_city = cnm + '/' + city + '/'

        #print('video location to delete : ',cnm_and_city)
        video = str(request.POST.get('Delete_now'))
        #print('Delete_now ',video)

        delete_video = str1 + cnm_and_city + video
        # delete_video = str1 + ' rb s3://' + name + ' --force'    # To delete bucket
        print(delete_video)
        os.system(delete_video)
        filename_processed_str = city +"_processed.csv"

        lines = list()
        members = video
        with open(filename_processed_str, 'r') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                lines.append(row)
                for field in row:
                    if field == members:
                        lines.remove(row)

        with open(filename_processed_str, 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)


        #filename_processed = open(filename_processed_str,"a")
#        updatedlist = []
#        with open(filename_processed_str, "r") as f:
#            reader = csv.reader(f)
            #video_title = input("Enter the username of the user you wish to remove from file:")

#            for row in reader:  # for every row in the file
#                if row[0] != video:  # as long as the username is not in the row .......
#                    updatedlist.append(row)  # add each row, line by line, into a list called 'udpatedlist'
#            print(updatedlist)
#            updatefile(filename_processed_str,updatedlist)

        list_bucket = 'aws s3 ls s3://ecube-eis/' + cnm_and_city + ' ' + '--recursive'
        #print(list_bucket)
        res = os.popen(list_bucket)
        res1 = list(res)
        #a = get_videos(res1,cnm,city)
        a = create_video_table_1(filename_processed_str)

        upload_csv_to_s3 = "aws s3 cp " + filename_processed_str + " " + "s3://all-signal-text-files"
        print(upload_csv_to_s3)
        tp = os.popen(upload_csv_to_s3)

        return render(request, 'listout_videos.html', {'show_table': a, 'cnm': cnm, 'city': city})
    else :
        return render(request, 'userpage.html')

    return render(request, 'userpage.html')

def updatefile(filename_processed, updatedlist):
    with open(filename_processed,"w",newline="") as f:
        Writer=csv.writer(f)
        Writer.writerows(updatedlist)
        print("File has been updated")

#def delete_expired_videos(current_user): 


def displaylist_user(request):
    # List all Objects in a Bucket Recursively
    # aws s3 ls s3://sbucket --recursive

    str1 = 'aws s3 ls s3://ecube-eis/'
    city_names = []
    if request.user.is_superuser:
        print("admin")
    else:
        current_user = request.user.username
        values = get_city_and_location(current_user)
        city_names = values['city_names']

    if request.method == 'POST':
        if request.user.is_superuser:
            print("its admin")
            signal_location = str(request.POST.get('location'))
            #print(location)
            cnm,location = signal_location.split('/')
            #print(cnm)
            #print(location)
        else:
            #print("\n#### List all objects in a bucket recursively ####\n")
            location = str(request.POST.get('location'))
            #print('location selected for listout : ',location)
            cnm = values['company_name']
            #print('cnm:', cnm)

        cmd = str1 + cnm + '/'
        list_bucket = cmd + location + ' ' + '--recursive'
        #print(list_bucket)
        res = os.popen(list_bucket)
        res1 = list(res)
        filename_processed_str = location + "_processed.csv"
        #a = get_videos(res1,cnm,location)
        a = create_video_table_1(filename_processed_str)

        upload_csv_to_s3 = "aws s3 cp " + filename_processed_str + " " + "s3://all-signal-text-files"
        print(upload_csv_to_s3)
        tp = os.popen(upload_csv_to_s3)
        return render(request, 'listout_videos.html', {'show_table':a, 'cnm':cnm , 'city': location})
    else:
        if request.user.is_superuser:
            return render(request, 'adminpage.html')
        else:
            return render(request, 'displaylist_user.html', {'city_names': city_names})

def displaylist_admin(request):
    full_list = get_all_clients_and_signals()
    #print("full list",full_list)
    return render(request, 'displaylist_admin.html',{"full_list": full_list}) 

def get_map1(request):
    return render(request,'get_map.html')

def get_map(request):
    if request.method == "POST":
        option = str(request.POST.get('choose'))
        print("option:",option)
        signal_name =  str(request.POST.get('signal_name'))
        current_user = request.user.username
        cnm = get_companyname(current_user)
        backslash= str('/')
        if option == 'listout':
	        cmd = "aws s3 ls s3://ecube-eis/" + cnm + backslash + signal_name
	        list_bucket = cmd + ' ' + '--recursive'
        	print(list_bucket)
	        res = os.popen(list_bucket)
	        res1 = list(res)
	        a = get_videos(res1, cnm, signal_name)

        	return render(request, 'listout_videos.html', {'show_table': a, 'cnm': cnm, 'city': signal_name})
        else:
            return render(request,'get_cctv_feeds.html')
    else:
        print('In else of get_map')

    return render(request,'get_map.html')


def get_cctv_feeds(request):
    img = 'static/images/smiley1.jpg'
    return render(request,'get_cctv_feeds.html',{'bgimg':img})

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "Forgot_password/password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'ecubesolutions.in',
                    'site_name': 'ecubesolutions.in',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'ecubesolutio99@gmail.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect("/")
                    #return redirect ("/password_reset/done/")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request= request, template_name="Forgot_password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"), required=True,
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"), required=True,
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

class PasswordResetConfirmView(FormView):
    template_name = "Forgot_password/password_reset_confirm.html"
    success_url = '/admin/'
    form_class = SetPasswordForm

    def form_valid(self, *arg, **kwargs):
        form = super(PasswordResetConfirmView, self).form_valid(*arg, **kwargs)
        uidb64=self.kwargs['uidb64']
        token=self.kwargs['token']
        UserModel = get_user_model()
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password= form.cleaned_data['new_password2']
            user.set_password(new_password)
            user.save()
            messages.success(self.request, 'Password reset has been successful.')
        else:
            messages.error(self.request, 'Password reset has not been unsuccessful.')
        return form

def admin_map(request):
    cmd = ''
    cmd = "ls /home/ubuntu/ecubesolutions.in/venv/smart_signal/static/images/maps"
    print(cmd)
    res = os.popen(cmd)
    res1 = list(res)

    return render(request,'admin_map.html',{'area_list':res1})

#def create_map(request):
#   return render(request,'create_map.html')

def test_session(request):
    request.session.set_test_cookie()
    return HttpResponse("Testing session cookie")


def test_delete(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        response = HttpResponse("Cookie test passed")
    else:
        response = HttpResponse("Cookie test failed")
    return response

def save_session_data(request):
    # set new data
    request.session['id'] = 1
    request.session['name'] = 'root'
    request.session['password'] = 'rootpass'
    return HttpResponse("Session Data Saved")

def access_session_data(request):
    response = ""
    if request.session.get('id'):
        response += "Id : {0} <br>".format(request.session.get('id'))
    if request.session.get('name'):
        response += "Name : {0} <br>".format(request.session.get('name'))
    if request.session.get('password'):
        response += "Password : {0} <br>".format(request.session.get('password'))

    if not response:
        return HttpResponse("No session data")
    else:
        return HttpResponse(response)


def delete_session_data(request):
    try:
        del request.session['id']
        del request.session['name']
        del request.session['password']
    except KeyError:
        pass

    return HttpResponse("Session Data cleared")

def lousy_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "root" and password == "pass":
            request.session['logged_in'] = True
            return redirect('lousy_secret')
        else:
            messages.error(request, 'Error wrong username/password')
    return render(request, 'layout1.html')


def lousy_secret(request):
    if not request.session.get('logged_in'):
        return redirect('adminpage')
    return render(request, 'layout1.html')


def lousy_logout(request):
    try:
        del request.session['logged_in']
    except KeyError:
        return redirect('layout1.html')
    return render(request, 'logout.html')
