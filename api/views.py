from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, UserProfile, Connection, Dislike
from rest_framework import generics, permissions
from knox.models import AuthToken
from rest_framework.response import Response
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import UserProfile
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer

from .models import Post
from .serializers import PostSerializer
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Like, Post
from rest_framework.permissions import IsAuthenticated
from .models import Connection
from .serializers import ConnectionSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView

from django.db.models import Count, Q



# Create your views here.

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })

# Profile View & Update API
class UserProfileAPI(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.userprofile


# Create Post API
class PostCreateAPI(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# List Posts API
class PostListAPI(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({"message": "You already liked this post."}, status=status.HTTP_200_OK)

        return Response({"message": "Post liked!"}, status=status.HTTP_201_CREATED)

class UnlikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({"message": "Post unliked."}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({"error": "You haven't liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        
class DislikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Remove like if exists
        Like.objects.filter(user=request.user, post=post).delete()
        
        dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({"message": "You already disliked this post."}, status=status.HTTP_200_OK)

        return Response({"message": "Post disliked!"}, status=status.HTTP_201_CREATED)

class UndislikePostAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            dislike = Dislike.objects.get(user=request.user, post=post)
            dislike.delete()
            return Response({"message": "Dislike removed."}, status=status.HTTP_200_OK)
        except Dislike.DoesNotExist:
            return Response({"error": "You haven't disliked this post."}, status=status.HTTP_400_BAD_REQUEST)
        
# Send a connection request
class SendConnectionRequestAPI(CreateAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = self.kwargs.get('user_id')
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if to_user == request.user:
            return Response({'error': 'Cannot connect to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        connection, created = Connection.objects.get_or_create(
            follower=request.user,
            following=to_user
        )

        if not created:
            return Response({'message': 'Connection request already sent or exists'}, status=status.HTTP_200_OK)

        return Response({'message': 'Connection request sent'}, status=status.HTTP_201_CREATED)

# View incoming connection requests
class IncomingConnectionRequestsAPI(ListAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Connection.objects.filter(
            following=self.request.user,
            status='pending'
        ).order_by('-created_at')

# Accept or decline a request
class RespondToConnectionRequestAPI(UpdateAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            connection = Connection.objects.get(id=pk, following=request.user)
        except Connection.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        status_choice = request.data.get('status')
        if status_choice not in ['accepted', 'declined']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        connection.status = status_choice
        connection.save()
        return Response({'message': f'Request {status_choice}'}, status=status.HTTP_200_OK)
    
class RecommendedUsersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Get all accepted connections
        connections = Connection.objects.filter(
            Q(follower=user) | Q(following=user),
            status='accepted'
        )

        connected_user_ids = set()
        for c in connections:
            connected_user_ids.add(c.follower.id if c.follower != user else c.following.id)

        # 2. Friends of friends
        friends_of_friends = Connection.objects.filter(
            status='accepted'
        ).filter(
            Q(follower__in=connected_user_ids) | Q(following__in=connected_user_ids)
        )

        # Set of second-degree connection IDs
        second_degree_ids = set()
        for conn in friends_of_friends:
            if conn.follower.id != user.id and conn.follower.id not in connected_user_ids:
                second_degree_ids.add(conn.follower.id)
            if conn.following.id != user.id and conn.following.id not in connected_user_ids:
                second_degree_ids.add(conn.following.id)

        # 3. Remove already connected, pending requests, and self
        pending_ids = set(Connection.objects.filter(
            Q(follower=user) | Q(following=user),
            status='pending'
        ).values_list('follower_id', 'following_id'))

        exclude_ids = connected_user_ids | {user.id}
        for pair in pending_ids:
            exclude_ids.update(pair)

        # Final recommended users
        recommended_users = User.objects.filter(id__in=second_degree_ids - exclude_ids)

        # Optional: sort by number of mutual connections
        mutual_counts = {}
        for u in recommended_users:
            mutuals = Connection.objects.filter(
                status='accepted'
            ).filter(
                Q(follower=user, following__in=[u]) | Q(following=user, follower__in=[u])
            ).count()
            mutual_counts[u.id] = mutuals

        recommended_users = sorted(
            recommended_users,
            key=lambda u: mutual_counts.get(u.id, 0),
            reverse=True
        )

        from .serializers import UserSerializer
        serializer = UserSerializer(recommended_users, many=True)
        return Response(serializer.data)

def home_view(request):
    return render(request, 'home.html')

@login_required
def feed_view(request):
    # Get users that the current user follows
    following = Connection.objects.filter(
        follower=request.user, 
        status='accepted'
    ).values_list('following', flat=True)
    
    # Get posts from those users and the current user
    posts = Post.objects.filter(
        Q(user__in=list(following)) | Q(user=request.user)
    ).order_by('-created_at')
    
    # Get likes and dislikes for each post
    for post in posts:
        post.liked_by_user = Like.objects.filter(post=post, user=request.user).exists()
        post.disliked_by_user = Dislike.objects.filter(post=post, user=request.user).exists()
        post.like_count = Like.objects.filter(post=post).count()
        post.dislike_count = Dislike.objects.filter(post=post).count()
    
    return render(request, 'feed.html', {'posts': posts})

@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    posts = Post.objects.filter(user=user).order_by('-created_at')
    
    # Count followers and following
    follower_count = Connection.objects.filter(following=user, status='accepted').count()
    following_count = Connection.objects.filter(follower=user, status='accepted').count()
    
    # Check if current user is following this profile
    is_following = Connection.objects.filter(follower=request.user, following=user, status='accepted').exists() if request.user.is_authenticated and request.user != user else False
    
    context = {
        'profile': profile,
        'posts': posts,
        'post_count': posts.count(),
        'follower_count': follower_count,
        'following_count': following_count,
        'is_following': is_following
    }
    
    return render(request, 'profile.html', context)

@login_required
def edit_profile_view(request):
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        profile.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            
        profile.save()
        
        # Update user information
        user = request.user
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
            
        user.save()
        
        # Redirect to profile view
        return redirect('profile_view')
    
    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def follow_user_view(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # Create or get connection
    connection, created = Connection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow,
        defaults={'status': 'accepted'}
    )
    
    if not created and connection.status != 'accepted':
        connection.status = 'accepted'
        connection.save()
    
    return redirect('profile_view', username=user_to_follow.username)

@login_required
def unfollow_user_view(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    # Delete connection
    Connection.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    
    return redirect('profile_view', username=user_to_unfollow.username)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check if passwords match
        if password != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})
        
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create user profile with a unique slug
            from django.utils.text import slugify
            import uuid
            
            base_slug = slugify(username)
            unique_id = str(uuid.uuid4())[:8]
            unique_slug = f"{base_slug}-{unique_id}"
            
            profile = UserProfile(user=user, slug=unique_slug)
            profile.save()
            
            # Log the user in
            login(request, user)
            
            # Redirect to feed
            return redirect('feed')
        except Exception as e:
            # If there's any error, delete the user if it was created
            if 'user' in locals():
                user.delete()
            return render(request, 'register.html', {'error': f'Registration failed: {str(e)}'})
    
    return render(request, 'register.html')

@login_required
def connections_view(request):
    # Get users that the current user follows
    following = Connection.objects.filter(
        follower=request.user, 
        status='accepted'
    ).select_related('following')
    
    # Get users that follow the current user
    followers = Connection.objects.filter(
        following=request.user, 
        status='accepted'
    ).select_related('follower')
    
    # Get pending connection requests
    pending_requests = Connection.objects.filter(
        following=request.user,
        status='pending'
    ).select_related('follower')
    
    context = {
        'following': following,
        'followers': followers,
        'pending_requests': pending_requests
    }
    
    return render(request, 'connections.html', context)

@login_required
def respond_to_request_view(request, request_id):
    if request.method == 'POST':
        try:
            connection = Connection.objects.get(id=request_id, following=request.user)
        except Connection.DoesNotExist:
            return redirect('connections_view')
        
        status_choice = request.POST.get('status')
        if status_choice in ['accepted', 'declined']:
            connection.status = status_choice
            connection.save()
        
        return redirect('connections_view')
    
    return redirect('connections_view')

@login_required
def recommend_users_view(request):
    # This is a simplified version of the RecommendedUsersAPI logic
    user = request.user
    
    # Get all accepted connections
    connections = Connection.objects.filter(
        Q(follower=user) | Q(following=user),
        status='accepted'
    )
    
    connected_user_ids = set()
    for c in connections:
        connected_user_ids.add(c.follower.id if c.follower != user else c.following.id)
    
    # Friends of friends
    friends_of_friends = Connection.objects.filter(
        status='accepted'
    ).filter(
        Q(follower__in=connected_user_ids) | Q(following__in=connected_user_ids)
    )
    
    # Set of second-degree connection IDs
    second_degree_ids = set()
    for conn in friends_of_friends:
        if conn.follower.id != user.id and conn.follower.id not in connected_user_ids:
            second_degree_ids.add(conn.follower.id)
        if conn.following.id != user.id and conn.following.id not in connected_user_ids:
            second_degree_ids.add(conn.following.id)
    
    # Remove already connected, pending requests, and self
    pending_ids = set(Connection.objects.filter(
        Q(follower=user) | Q(following=user),
        status='pending'
    ).values_list('follower_id', 'following_id'))
    
    exclude_ids = connected_user_ids | {user.id}
    for pair in pending_ids:
        exclude_ids.update(pair)
    
    # Final recommended users
    recommended_users = User.objects.filter(id__in=second_degree_ids - exclude_ids)[:20]
    
    context = {
        'recommended_users': recommended_users
    }
    
    return render(request, 'recommendations.html', context)

@login_required
def like_post_view(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return redirect('feed')
            
        # Check if already liked
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('feed')
    return redirect('feed')

@login_required
def unlike_post_view(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
        except (Post.DoesNotExist, Like.DoesNotExist):
            pass
            
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('feed')
    return redirect('feed')

@login_required
def create_post_view(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if content:
            post = Post(user=request.user, content=content)
            
            if 'image' in request.FILES:
                post.image = request.FILES['image']
                
            post.save()
            
        return redirect('feed')
    return redirect('feed')

@login_required
def dislike_post_view(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            # Remove like if exists
            Like.objects.filter(user=request.user, post=post).delete()
            
            # Add dislike
            dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
        except Post.DoesNotExist:
            pass
            
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('feed')
    return redirect('feed')

@login_required
def undislike_post_view(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            dislike = Dislike.objects.get(user=request.user, post=post)
            dislike.delete()
        except (Post.DoesNotExist, Dislike.DoesNotExist):
            pass
            
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('feed')
    return redirect('feed')

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    """
    Custom logout view that logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect('home')
