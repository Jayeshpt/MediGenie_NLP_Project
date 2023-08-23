from django.urls import path
from.import views
urlpatterns = [
    path('',views.index,name='index'),
    path('chatbot/',views.chatbot,name='chatbot'),
    path('upload/', views.upload_file, name='upload_file'),
    path('data_table/', views.show_data, name='show_data'),
    path('get_response', views.get_response, name='get_response'),
    

    
    
]
