from django.urls import path

from . import views
from .views import LoginView, RegisterView, UploadFileView, CreateFolderView

urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(), name='login'),
    path('create_account', RegisterView.as_view(), name='create_account'),
    path('logout', views.logout_view, name='logout'),
    path('upload_file', UploadFileView.as_view(), name='upload_file'),
    path('create_folder', CreateFolderView.as_view(), name='create_folder'),
    path('files/<int:id>/<int:folder>', views.files, name='files'),
    path('view_file/<int:id>', views.view_file, name='view_file'),
    path('download_file/<int:id>', views.download_file, name='download_file'),
    path('delete_file/<int:id>', views.delete_file, name='delete_file'),
    path('search_user_files/<int:user_id>', views.search_user_files, name='search_user_files'),
    path('search_all_files', views.search_all_files, name='search_all_files')
]
