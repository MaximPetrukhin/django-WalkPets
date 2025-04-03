from django.shortcuts import render

def index(requests):
    return render(requests, "services/index.html")

def services(requests):
    return render(requests, "services/services.html")