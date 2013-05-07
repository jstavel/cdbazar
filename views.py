#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.utils.decorators import classonlymethod
from django.template import loader, Context, RequestContext
from django.views.generic import TemplateView, View

import json,os
from django.http import HttpResponse


class ViewWithSubView(TemplateView):
    """ vrati funkci, ktera rozhodne, jestli se pohled zapouzdri do celkove sablony
    - normalni html reguest,
    nebo se vrati jen to, co pohled vyrenderuje. Vrati to jako html.
    
    Druhy zpusob se pouzije v pripade, ze se toto volalo pres ajaxe.

    Pohledy se predavaji jako argumenty ve tvaru:

    view_main ... view_ je povinne
              ... main je nazev slotu v base.html
    view_sidebar ... view na leve strane
    view_navigation ... view pred hlavnim obsahem
    """
    view_main = []
    view_sidebar = []
    view_navigation = []

    def get_context_data(self, **kwargs):
        context = {} #super(TemplateView,self).get_context_data(**kwargs)
        for nn in [vv for vv in dir(self) if vv.startswith("view_") ]:
            views,name = getattr(self,nn), nn.split("_")[1]
            context[name] = ""
            for view in views:
                response = view(self.request, *self.args, **self.kwargs)
                response.render()
                context[name] += response.content
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class SearchView(TemplateView):
    template_name = "search.html"
    pass

class AjaxDispatcher(View):
    for_ajax = None
    for_others = None

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.for_ajax(request,*args,**kwargs)
        return self.for_others(request,*args,**kwargs)

class JSONTemplateResponse(object):
    """
    A mixin that can be used to render a JSON response.
    """
    page_includes = []
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(self.render_to_json(context),**response_kwargs)

    def render_to_json(self, context):
        my_context =  isinstance(context, Context) and context or RequestContext(self.request, context)
        data = {}

        for include in self.page_includes:
            content = loader.get_template(include)
            data[include] = content.render(my_context)
            
        return json.dumps(data)

def prepare_render_to_response(class_for_json, class_for_http):
    def render_to_response(self, context, **response_kwargs):
        if( self.request.is_ajax() ):
            return class_for_json.render_to_response(self, context, **response_kwargs)
        else:
            return class_for_http.render_to_response(self, context, **response_kwargs)
    return render_to_response
