from django.shortcuts import render


def main(request):
    context = {'title': 'Delta',
               'description': 'Delta main page'}
    return render(request, 'delta/main_delta.html', context)


