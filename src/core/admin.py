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


# class BudgetTagInline(admin.TabularInline):
#     model = models.BudgetTag
#     extra = 0
#
#
# class SpendingInline(admin.TabularInline):
#     model = models.Spending
#     ordering = ('-id',)
#     extra = 0
#
#
# class BudgetAdmin(admin.ModelAdmin):
#     ordering = ['start_date', 'id']
#     list_display = ['start_date', 'end_date']
#     inlines = (BudgetTagInline, SpendingInline,)
#     fieldsets = (
#         (None, {'fields': ('start_date', 'end_date')}),
#     )
#
admin.site.register(models.User, UserAdmin)
# admin.site.register(models.Budget, BudgetAdmin)
admin.site.register(models.Tag)
