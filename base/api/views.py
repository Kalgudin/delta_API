from django.shortcuts import render


def main(request):
    context = {'title': 'API',
               'description': 'API main page'}
    return render(request, 'api/main_API.html', context)

