import os

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, FileResponse
from django.utils.encoding import smart_str
from .models import File, Folder

def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html', {'user': request.user})
    return redirect('login')

class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return redirect('login')

class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        email = request.POST['email']
        if User.objects.filter(username=email):
            return redirect('create_account')
        nome = request.POST['nome']
        password = request.POST['password']
        user = User.objects.create_user(email, nome, password)
        os.makedirs('app/users/' + str(user.id))
        user.first_name = nome
        user.save()
        login(request, user)
        return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('login')

class UploadFileView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'upload_file.html', {'user': request.user, 'folders': Folder.objects.filter(owner=request.user.id)})
        return redirect('login')

    def post(self, request):
        file = request.FILES['file']
        under = request.POST['under']
        under = Folder.objects.get(id=under, owner=request.user)
        name = request.POST['name']
        privacy = request.POST.get('privacy', False);
        name_in_dir = file.name.replace(' ', '')
        caminho = 'app/users/' + str(request.user.id) + '/' + name_in_dir
        with open(caminho, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        f = File(name=name, name_in_dir=name_in_dir, privacity=privacy, under=under, uploaded_by=request.user)
        f.save()
        return redirect('/files/' + str(request.user.id) + '/0')

class CreateFolderView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'create_folder.html', {'user': request.user, 'folders': Folder.objects.filter(owner=request.user.id)})
        return redirect('login')

    def post(self, request):
        under = request.POST['under']
        name = request.POST['name']
        f = Folder(name=name, owner=request.user, under=int(under))
        f.save()
        return redirect('/files/' + str(request.user.id) + '/0')

def folders_path(folder):
    a = []
    while folder.under != 0:
        a.append({'name': folder.name, 'link': f"/files/{folder.owner.id}/{folder.id}"})
        folder = Folder.objects.get(id=folder.under)
    a.append({'name': folder.name, 'link': f"/files/{folder.owner.id}/{folder.id}"})
    a.append({'name': 'Root', 'link': f"/files/{folder.owner.id}/0"})
    a = reversed(a)
    return a
    #if int(folder) == 0:
    #    return []
    #folder = Folder.objects.get(id=int(folder))
    #print({'name': folder.name, 'link': f"/files/{folder.owner.id}/{folder.id}"})
    #return folders_path(folder.under).append({'name': folder.name, 'link': f"/files/{folder.owner.id}/{folder.id}"})

def files(request, id, folder):
    folders = Folder.objects.filter(owner=id, under=folder)
    state_folder = None
    folders_p = []
    if folder == 0:
        state_folder = {'name': 'Root'}
        folders_p.append({'name': 'Root', 'link': f"/files/{id}/{folder}"})
    else:
        state_folder = Folder.objects.get(id=folder)
        folders_p = folders_path(state_folder)
    files = None
    user = None
    if id == request.user.id:
        user = request.user
        files = File.objects.filter(uploaded_by=id, under=folder)
    else:
        files = File.objects.filter(uploaded_by=id, privacity=1, under=folder)
    return render(request, 'archives.html', {'user': user, 'folders_p': folders_p, 'folders': folders, 'files': files})

def view_file(request, id):
    file = File.objects.get(id=id)
    if request.user.is_authenticated and (file.privacity == "1" or file.uploaded_by_id == request.user.id):
        file_path = 'app/users/' + str(file.uploaded_by_id) + '/' + file.name_in_dir
        f = open(file_path, 'rb')
        #print(file.name_in_dir)
        response = FileResponse(f)
        #print(str(response.filename))
        return response
    else:
        return HttpResponse('file is not avaliable for you.')

def download_file(request, id):
    file = File.objects.get(id=id)
    if request.user.is_authenticated and (file.privacity == "1" or file.uploaded_by_id == request.user.id):
        file_path = 'app/users/' + str(file.uploaded_by_id) + '/' + file.name_in_dir
        f = open(file_path, 'rb')
        response = FileResponse(f, content_type='application/force-download')
        #response['Content-Disposition'] = 'inline; filename=' + file.name_in_dir
        return response
    else:
        return HttpResponse('file is not avaliable for you.')

def delete_file(request, id):
    file = File.objects.get(id=id)
    if request.user.is_authenticated and (file.privacity == "1" or file.uploaded_by_id == request.user.id):
        file_path = 'app/users/' + str(file.uploaded_by_id) + '/' + file.name_in_dir
        f = os.remove(file_path)
        file.delete()
        #response = FileResponse(f, content_type='application/force-download')
        #response['Content-Disposition'] = 'inline; filename=' + file.name_in_dir
        return redirect('index')
    else:
        return HttpResponse('file is not avaliable for you.')


def search_user_files(request, user_id):
    name = request.GET['search']
    files = File.objects.filter(uploaded_by=request.user.id, name__startswith=name)
    return render(request, 'archives.html', {'user': request.user, 'search': name, 'files': files})

def search_all_files(request):
    try:
        name = request.GET['search']
        user_files = File.objects.filter(name__startswith=name, uploaded_by=request.user.id)
        files = File.objects.filter(name__startswith=name, privacity=1)
        return render(request, 'archives.html', {'user': None, 'search': name, 'user_files': user_files, 'files': files})
    except Exception as e:
        return render(request, 'archives.html', {'user': None})
