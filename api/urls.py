from django.urls import path, include
from knox import views as knox_views
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from .views import RegisterAPI, UserProfileAPI
from .views import PostCreateAPI, PostListAPI
from .views import LikePostAPI, UnlikePostAPI
from .views import SendConnectionRequestAPI, IncomingConnectionRequestsAPI, RespondToConnectionRequestAPI
from .views import RecommendedUsersAPI

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'logout': reverse('logout', request=request, format=format),
        'profile': reverse('user_profile', request=request, format=format),
        'posts': reverse('post_list', request=request, format=format),
        'create_post': reverse('post_create', request=request, format=format),
        'recommendations': reverse('recommend_users', request=request, format=format),
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('register/', RegisterAPI.as_view(), name='api_register'),
    path('login/', KnoxLoginView.as_view(), name='api_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='api_logout'),
    path('profile/', UserProfileAPI.as_view(), name='user_profile'),
]

urlpatterns += [
    path('posts/', PostListAPI.as_view(), name='post_list'),
    path('posts/create/', PostCreateAPI.as_view(), name='post_create'),
    path('posts/<int:post_id>/like/', LikePostAPI.as_view(), name='like_post'),
    path('posts/<int:post_id>/unlike/', UnlikePostAPI.as_view(), name='unlike_post'),
    path('connections/send/<int:user_id>/', SendConnectionRequestAPI.as_view(), name='send_connection'),
    path('connections/requests/', IncomingConnectionRequestsAPI.as_view(), name='incoming_requests'),
    path('connections/respond/<int:pk>/', RespondToConnectionRequestAPI.as_view(), name='respond_request'),
    path('recommendations/', RecommendedUsersAPI.as_view(), name='recommend_users'),
]
