from garpix_utils.logs.enums.get_enums import Action, ActionResult
from garpix_utils.logs.loggers import ib_logger
from garpix_utils.logs.mixins.create_log import CreateLogMixin
from garpix_utils.logs.services.logger_iso import LoggerIso
from garpix_utils.models import AdminDeleteMixin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from garpix_user.utils.get_password_settings import get_password_settings


class UserAdmin(AdminDeleteMixin, BaseUserAdmin, CreateLogMixin):
    change_form_template = "garpix_user/send_confirm.html"

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_deleted', 'is_staff', 'is_superuser',
                'is_blocked', 'login_attempts_count', 'password_updated_date', 'needs_password_update',
                'groups', 'user_permissions', 'keycloak_auth_only'
            ),
        }),
        (_('Viber'), {
            'fields': ('viber_chat_id', 'viber_secret_key',)
        }),
        (_('Telegram'), {
            'fields': ('telegram_chat_id', 'telegram_secret', 'get_telegram_connect_user_help'),
        }),
        (_('Confim information'), {
            'fields': (
                'is_email_confirmed', 'email_confirmation_code', 'is_phone_confirmed', 'phone_confirmation_code'),
        }),
    )
    readonly_fields = ['telegram_secret', 'get_telegram_connect_user_help'] + list(BaseUserAdmin.readonly_fields)

    def delete_model(self, request, obj):
        action = Action.user_delete.value
        log = self.log_delete(ib_logger, request, obj, action)
        super().delete_model(request, obj)
        ib_logger.write_string(log)

    def delete_queryset(self, request, queryset):
        action = Action.user_delete.value
        logs = []
        for obj in queryset:
            logs.append(self.log_delete(ib_logger, request, obj, action))
        super().delete_queryset(request, queryset)
        for log in logs:
            ib_logger.write_string(log)

    def save_model(self, request, obj, form, change):
        password_first_change = get_password_settings()['password_first_change']

        if not change and password_first_change:
            obj.needs_password_update = True

        log = self.log_change_or_create(ib_logger, request, obj, change,
                                        action_change=Action.user_change.value,
                                        action_create=Action.user_create.value)
        ib_logger.write_string(log)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        obj = form.instance
        prev_groups = set()
        if change:
            prev_groups = set([str(_obj) for _obj in obj.groups.all()])
            log = self.log_change_m2m_field(ib_logger, request, super(), form, formsets, change,
                                            action_change=Action.user_change.value,
                                            exclude_fields=['groups'])
            if log:
                ib_logger.write_string(log)

        else:
            super().save_related(request, form, formsets, change)

        groups = set([str(_obj) for _obj in obj.groups.all()])

        new_old = groups - prev_groups
        old_new = prev_groups - groups

        msg = CreateLogMixin.log_msg_change if CreateLogMixin.log_msg_change else f'Объект {str(obj)}(id={obj.pk}) модели {obj.__class__.__name__} был изменен'

        if new_old or old_new:
            if new_old:
                log = ib_logger.create_log(action=Action.group_add_user.value,
                                           obj=obj.__class__.__name__,
                                           obj_address=request.path,
                                           result=ActionResult.success,
                                           sbj=request.user.username,
                                           params=f'группы: {new_old}',
                                           sbj_address=LoggerIso.get_client_ip(request),
                                           msg=msg)
                ib_logger.write_string(log)
            if old_new:
                log = ib_logger.create_log(action=Action.group_delete_user.value,
                                           obj=obj.__class__.__name__,
                                           obj_address=request.path,
                                           result=ActionResult.success,
                                           sbj=request.user.username,
                                           params=f'группы: {old_new}',
                                           sbj_address=LoggerIso.get_client_ip(request),
                                           msg=msg)
                ib_logger.write_string(log)
