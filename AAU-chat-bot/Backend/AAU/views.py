from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .main import MyAI, clear_memory

def clear_chat(request):
    session_id = request.GET.get("session_id", "default")

    clear_memory(session_id)

    return JsonResponse({"status": "cleared"})

def stream_answer(request):
    question = request.GET.get('question','')
    session_id = request.GET.get('session_id','default')

    ai = MyAI(question,session_id)
    answer = ai.respond()
    return JsonResponse({"answer":answer},safe=False)


# Create your views here.
