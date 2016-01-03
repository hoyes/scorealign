from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.conf.urls.static import static

urlpatterns = patterns('scorealign.views',
	url(r'^$', 'index'),
	url(r'^audio/(?P<name>.*).wav', 'audio'),
	url(r'^scoredata/(?P<name>.*).json', 'scoredata'),
	url(r'^align/(?P<likelihood>.*)/(?P<path>.*)/(?P<name>.*).json', 'align'),
)
