from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from .forms import LoginForm


def logoutaccount(request):
    logout(request)
    
    return redirect('home')

def loginaccount(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Неправильное имя пользователя или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'loginaccount.html', {'form': form})