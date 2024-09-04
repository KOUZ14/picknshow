from django.shortcuts import render

# Create your views here.
def serve_template(request):
    return render(request, 'landing/home.html')
