from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')
def browse_cases(request):
    return render(request, 'browse_cases.html')