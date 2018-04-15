from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

from django.conf.urls import url

app_name = 'system'

urlpatterns = [
	# This is the first page when user doesn't have any extension and will be redirected to login page
    path('', views.blank, name='blank'),

	# Login Page
	path('login',auth_views.login),

	# Logout Page
	url(r'^logout/$', views.logout, {'next_page': '/'}, name='logout'),

	# Main page after login with checking at views.py
    path('home',views.main_page, name='home'),

	# Add Report
	url( r'report/add/$', views.ReportView.as_view(), name='report-add'),

    url( r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # Pull all reports belonging to the supervisor
    url( r'^ajax/supervisor_reports/$', views.retrieveSupervisorReports, name='supervisorReports'),

    # Check if CMO LO authentication
    url( r'^ajax/check_Authentication/$', views.checkAccountAuth, name='checkAuthentication'),

    #Pull all reports
    url(  r'^ajax/all_reports/$', views. retrieveAllReports, name='allReports'),

    #Modify Report
	url(  r'^ajax/modify_Report/$', views.modifyReport, name='modifyReport'),

    #Delete Report
    url(  r'^delete_report/(?P<myPk>[0-9]+)/$', views. deleteReport, name='deleteReport'),

    #Send to CMO
    url(  r'^send_to_CMO/(?P<myPk>[0-9]+)/$', views.sendToCMO, name='sendToCMO'),

    # API for CMO to pull reports
    url('test/(?P<token>[\w\.-]+)', views.CMOPull, name='CMOPull')
]
