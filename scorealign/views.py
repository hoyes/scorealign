from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.views.decorators.cache import cache_page

import data, os, json
import alignment

def index(request):
	return render_to_response('scorealign/index.html', {"files": data.names() }, context_instance=RequestContext(request))

#@cache_page(60*60*48)
def audio(request, name):
    filename = data.get_path(name) + '.wav'                                
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='audio/wav')
    response['Content-Length'] = os.path.getsize(filename)
    return response
    
@cache_page(60*60*48)
def scoredata(request, name):
    audio = data.get_audio(name, 0.0)
    score = data.get_score(name, audio.total_length)
    output = {'events': score.events(), 'duration': score.length(), 'note_range': score.note_range()}
    return HttpResponse(json.dumps(output))

def truth(request, seconds, name):
    truth = data.get_truth(name, seconds)

#@cache_page(60*60)
def align(request, likelihood, path, name):
    
    a = alignment.align(name, likelihood, path, rel_width=0.3)

    score = data.get_score(name)
    audio_points, score_points = a.get_events(score)

    return HttpResponse(json.dumps({'audio': audio_points, 'score': score_points, 
        'duration': score.length()}))
