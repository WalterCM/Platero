from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )


class TermTagInline(admin.TabularInline):
    model = models.TermTag
    extra = 0


class SpendingInline(admin.TabularInline):
    model = models.Spending
    ordering = ('-id',)
    extra = 0


class TermAdmin(admin.ModelAdmin):
    ordering = ['start_date', 'id']
    list_display = ['start_date', 'end_date']
    inlines = (TermTagInline, SpendingInline,)
    fieldsets = (
        (None, {'fields': ('start_date', 'end_date')}),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Term, TermAdmin)
admin.site.register(models.Tag)
