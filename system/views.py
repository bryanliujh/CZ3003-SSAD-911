from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import IncidentReport
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views import generic
from .forms import AddReportForm
import requests

def blank(request):
    return redirect('/login')

# Create your views here.
def main_page(request):
    global queuedReportsList
    global mylist

    context = {  # some data we might wanna pass over
        'username': request.user.get_username,
        'all_reports': IncidentReport.objects.all()
    }

    #check the user is logged in
    #else redirect to login page
    if request.user.is_authenticated:
        # retrieve the person's role and redirect accordingly
        if(request.user.role.job == 'operator'):
            return render(request, 'system/operator.html', context)
        elif(request.user.role.job == 'supervisor'):
            mylist.add_user(request.user.get_username())

            #event that there are reports from when oeprators submit reports while there are no supervisors online
            #assign them all to the guy who logs in and empty the list
            if(len(queuedReportsList) > 0):
                for i in queuedReportsList:
                    i.assigned_to_supervisor = request.user.get_username()
                    i.save()
                queuedReportsList = []

            return render(request, 'system/supervisor.html', context)
        else:
            return redirect('/login')
    else:
        return redirect('/login')

from django.contrib.auth import views as auth_views
from django.contrib.auth.views import logout
def logout(request, next_page):
    if(request.user.role.job == 'supervisor'):
        mylist.remove_user(request.user.get_username())
    return auth_views.logout(request, next_page)


class ReportView( generic.TemplateView ):
    template_name = 'system/incidentreport_form.html'

    def get( self, request ):
        form = AddReportForm()
        return render( request, self.template_name, {'form': form} )

    def post( self, request ):
        form = AddReportForm( request.POST )
        if form.is_valid(): #code for saving a form to the database
            post = form.save(commit=False)
            post.user = request.user
            post.status = 'pending'

            #not really used??
            phone_number = form.cleaned_data['phone_number']
            title = form.cleaned_data['title']
            detail = form.cleaned_data['detail']
            location = form.cleaned_data['location']
            emergency_level = form.cleaned_data['emergency_level']
            longitude = form.cleaned_data['longitude']
            latitude = form.cleaned_data['latitude']

            supervisorToAssignTo = mylist.get_next_in_list()
            if(supervisorToAssignTo == ''):
                post.assigned_to_supervisor = ''
                queuedReportsList.append(post)
            else:
                post.assigned_to_supervisor = supervisorToAssignTo

            form.save()
            return redirect( 'system:home' )
        #in event the form is invalid, return him to his current page?
        args = { 'form': form, 'phone_number': phone_number, 'title': title, 'detail': detail, 'location': location, 'emergency_level': emergency_level, 'longitude':longitude, 'latitude':latitude}
        return render( request,self.template_name, args )


class DetailView( generic.DetailView ):
    model = IncidentReport
    template_name = 'system/detail.html'



class OnlineList:
  def __init__(self):
    self.supervisor_list = []
    pass

  def add_user(self, x):
      if(x not in self.supervisor_list):
          self.supervisor_list.insert(0, x)
          print("Online Users: ", self.supervisor_list)

  def remove_user(self, x):
    if(x in self.supervisor_list):
        self.supervisor_list.remove(x)
        print(x, "went offline!")


  def get_next_in_list(self):
      #in event there is no supervisors online
      if(len(self.supervisor_list) == 0): return ''
      user = self.supervisor_list.pop(0)
      self.supervisor_list.append(user)
      return user

mylist = OnlineList()
queuedReportsList = []

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json

#For CMO LO authentication widget
def checkAccountAuth(request):
    postUsername = request.POST.get( 'uname' )
    postPassword = request.POST.get( 'psw' )
    myPk = request.POST.get('pk')
    user = authenticate( username=postUsername, password=postPassword )

    if user is not None:
        result = User.objects.filter( username=postUsername, password=postPassword )
        report = IncidentReport.objects.get(pk=myPk)
        report.status = 'authenticatedByCMOLO'
        report.save()
        return HttpResponse(serialize('json', result, cls=DjangoJSONEncoder), content_type="application/json")

    return HttpResponse( 'No user found', status=401 )

from itertools import chain

def retrieveSupervisorReports(ajaxObject):
    username = ajaxObject.GET.get('username', None)
    result = IncidentReport.objects.filter(assigned_to_supervisor=username, status='pending') #.order_by('-emergency_level')
    result2 = IncidentReport.objects.filter(assigned_to_supervisor=username, status='authenticatedByCMOLO').order_by('-emergency_level')
    result_list = list(chain(result, result2))
    return HttpResponse(serialize('json', result_list, cls=DjangoJSONEncoder), content_type="application/json")

def retrieveAllReports(x):
    result = IncidentReport.objects.all()
    return HttpResponse(serialize('json', result, cls=DjangoJSONEncoder), content_type="application/json")

def modifyReport(request):
    id = request.POST.get("pk")
    title = request.POST.get("title")
    detail = request.POST.get("detail")
    location = request.POST.get("location")
    emergency_level = request.POST.get("emergency_level")

    #modify report in DB
    result = IncidentReport.objects.all()
    report = IncidentReport.objects.get(pk=id)
    report.location = location
    report.emergency_level = emergency_level
    report.status = 'pending'
    report.title = title
    report.detail = detail
    report.save()
    return HttpResponse(serialize('json', result, cls=DjangoJSONEncoder), content_type="application/json")

def deleteReport(request, myPk):
    #delete report in DB
    report = IncidentReport.objects.get(pk=myPk)
    report.delete()

    # redirect user back to his page
    context = {
        'username': request.user.get_username
    }
    return render(request, 'system/supervisor.html', context)

def sendToCMO(request, myPk):
    report = IncidentReport.objects.get(pk=myPk)
    report.status = 'loadedToAPI'
    report.save()
    context = {
        'username': request.user.get_username
    }
    return render(request, 'system/supervisor.html', context)

    ''' Not needed anymore, since we are doing GET
    # create an object to send, with the fields as agreed by the other team leads
    objectToSend = {}
    #  objectToSend['incident_id'] = report.pk
    #  objectToSend['incident_date_time'] = str(report.datetime)
    #  objectToSend['incident_phone'] = report.phone_number
    objectToSend['location'] = report.location
    objectToSend['detail'] = report.detail
    objectToSend['title'] = report.title
    # objectToSend['incident_NRIC'] = report.nric
    objectToSend['emergency_level'] = report.emergency_level
    objectToSend = json.dumps(objectToSend)

    # send to CMO, check with Hans for CMO's URL
    # with a POST request, rmb to set (Static) token for verification
    try:
        response = requests.post(
            'http://10.27.241.103:8000/api/notifs/?username=911&api_key=84a639c34e3b103172cbe1738e00b5edbeb0fb11',
            headers={'Content-Type': 'application/json'}, data=objectToSend)
        reply = response.content  # handle acknowledge? ignore for now
    except:
        print("error in sending!")
    # redirect user back to his page
    context = {
        'username': request.user.get_username
    }
    return render(request, 'system/supervisor.html', context)
    '''



#CMO is to GET from us
#only the fields: location, detail, title, emergency_level, lat, lon
#datetime, pk/id?
def CMOPull(request, token):
    if(token == '84a639c34e3b103172cbe1738e00b5edbeb0fb11'):
        reports = IncidentReport.objects.filter(status='loadedToAPI', emergency_level=3)
        dataToSend = reports.only('location', 'detail', 'title', 'emergency_level','latitude', 'longitude')
        dataToSend = serialize('json', dataToSend, cls=DjangoJSONEncoder)
        print('json to send:', dataToSend)
        #reports.update(status='sentToCMO') #disable for initial GET testing, as the reports will always disappear
        print(reports)
        return HttpResponse(dataToSend, content_type='application/json')
    else:
        return HttpResponse('Token Authentication Error!')
    ''' to call our GET API, the following code should work
    response = requests.get('http://localhost:8080/test',  headers={'Content-Type': 'application/json'})
    import json
    reply = json.loads(response.content)
    print(reply)
    '''


'''
#for testing only
def CMOPull(request):
    reports = IncidentReport.objects.filter(status='sentToCMO')
    dataToSend = serialize('json', reports, cls=DjangoJSONEncoder)
    return HttpResponse(dataToSend, content_type='application/json')
'''