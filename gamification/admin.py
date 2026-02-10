from django.contrib import admin
from .models import Badge, UserBadge, JetWallet, JetTransaction, Reward, RewardRedemption


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_value']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_at']
    list_filter = ['badge']


@admin.register(JetWallet)
class JetWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'total_earned', 'total_spent', 'level', 'updated_at']
    list_filter = ['level']
    search_fields = ['user__username']
    readonly_fields = ['total_earned', 'total_spent']


@admin.register(JetTransaction)
class JetTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['description']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'stock', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['price', 'is_active', 'stock']


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'redeemed_at']
    list_filter = ['reward', 'redeemed_at']
