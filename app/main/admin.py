from django.contrib import admin
from .models import Machine, Maintenance, Reference, Reclamation, MyUser
from .forms import MachineModelForm, ReclamationModelForm, MaintenanceModelForm, MyUserCreationForm, MyUserChangenForm
from django.contrib.auth.admin import UserAdmin


class MachineModelAdmin(admin.ModelAdmin):
    form = MachineModelForm


class ReferenceModelAdmin(admin.ModelAdmin):
    list_filter = ["ref_type"]


class MaintenanceModelAdmin(admin.ModelAdmin):
    form = MaintenanceModelForm


class ReclamationModelAdmin(admin.ModelAdmin):
    form = ReclamationModelForm


class MyUserAdmin(UserAdmin):
    add_form = MyUserCreationForm
    form = MyUserChangenForm
    model = MyUser
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", 'user_type', "user_ref")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", 'user_type', "user_ref", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Machine, MachineModelAdmin)
admin.site.register(Maintenance, MaintenanceModelAdmin)
admin.site.register(Reference, ReferenceModelAdmin)
admin.site.register(Reclamation, ReclamationModelAdmin)
