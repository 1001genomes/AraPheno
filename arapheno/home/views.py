from django.shortcuts import render
from django.shortcuts import render

from forms import GlobalSearchForm

'''
Home View of AraPheno
'''
def home(request):
    search_form = GlobalSearchForm()
    return render(request,'home/home.html',{"search_form":search_form})

'''
About Information View of AraPheno
'''
def about(request):
    return render(request,'home/about.html',{})

