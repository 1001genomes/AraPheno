from django.shortcuts import render
from django.shortcuts import render

'''
Home View of AraPheno
'''
def home(request):
    return render(request,'home/home.html',{})

'''
About Information View of AraPheno
'''
def about(request):
    return render(request,'home/about.html',{})

