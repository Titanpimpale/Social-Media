from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Post, Like, Connection

# Define inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register Post model
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_preview', 'has_image', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

# Register Like model
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'

# Register Connection model
@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('follower__username', 'following__username')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    actions = ['accept_connections', 'decline_connections']
    
    def accept_connections(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} connections were successfully accepted.')
    accept_connections.short_description = "Accept selected connections"
    
    def decline_connections(self, request, queryset):
        updated = queryset.update(status='declined')
        self.message_user(request, f'{updated} connections were successfully declined.')
    decline_connections.short_description = "Decline selected connections"
