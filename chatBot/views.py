# -*- coding:utf-8 -*-


from django.http import HttpResponse
import json

import sys
sys.path.append('../')
from presses import nlp_presses

def get_response(request):
    answer_dict = {}
    if request.method == 'GET':
        # http://127.0.0.1:8000/answer?q=*****
        value = request.GET.get('q')
        seq_dict = nlp_presses.re_to_api(value)
        if value != '':
            answer_dict = seq_dict
            # if seq_dict['code'] != 1:
            #     answer_dict['code'] = 0
            #     answer_dict['content'] = 'no answer!'
            # else:
            #     answer_dict['code'] = 1
            #     answer_dict['content'] = seq

        else:
            answer_dict['code'] = 0
            answer_dict['content'] = "failed"
    else:
        value = "failed"

    return HttpResponse(json.dumps(answer_dict))