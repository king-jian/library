from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', welcome_page, name='welcome_page'),
    url(r'^welcome$', welcome_page, name='welcome_page'),
    url(r'^login/$', login_page, name='login_page'),
    url(r'^login/1$', login_action, name='login_action'),
    url(r'^signup/$', signup_page, name='signup_page'),
    url(r'^signup/1$', signup_action, name='signup_action'),
    url(r'^logout/$', logout_action, name='logout_action'),
    url(r'^index/$', index, name='index'),
    url(r'^bookslist/$', bookslist, name='bookslist'),
    url(r'^record/$', record_page,name='record_page'),
    url(r'^record/delete(?P<record_id>[0-9]+)$', delete_waiting,name='delete_waiting'),
    url(r'^book/(?P<book_id>[0-9]+)$', book_page, name='book_page'),
    url(r'^record/borrow$', borrow_action,name='borrow_action'),
    url(r'^bookslist/search/$', search_action,name='search_action'),
    url(r'^settings/$', setting, name='settings'),

]
