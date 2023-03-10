from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def view_404(request, exception=None):
    return render(request, 'index.html')