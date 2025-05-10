from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Post, Like, Connection


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'profile_picture', 'slug']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'created_at', 'like_count']

    def get_like_count(self, obj):
        return Like.objects.filter(post=obj).count()

class ConnectionSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Connection
        fields = ['id', 'follower', 'following', 'status', 'created_at']


