from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'fitness_goal', 'created_at')
    list_filter = ('fitness_goal', 'created_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')
        }),
        ('Fitness Information', {
            'fields': ('height', 'weight', 'fitness_goal')
        }),
        ('Additional Information', {
            'fields': ('bio', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
