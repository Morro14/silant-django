from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


# Create your models here.
class MyUser(AbstractBaseUser, PermissionsMixin):
    def __str__(self):
        return self.email

    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    types = {
        'client': 'Client',
        'service': 'Service company',
        'manager': 'Manager'
    }

    user_type = models.TextField(max_length=120, default="not specified", choices=types, verbose_name="User type")
    user_ref = models.OneToOneField(to='Reference', on_delete=models.CASCADE, blank=True, null=True,
                                    verbose_name="Organization or IP")


class Reference(models.Model):
    types = {
        'service_company': 'Service company',
        'client': 'Client',
        'machine_model': ' Machine model',
        'engine_model': 'Engine model',
        'transmission_model': 'Transmission model',
        'steerable_bridge_model': 'Steerable bridge model',
        'main_bridge_model': 'Main bridge model',
        'not_specified': 'not specified',
        'failure_node': 'Failure node',
        'recovery_method': 'Recovery method',
        'maintenance_type': 'Maintenance type'

    }

    def __str__(self):
        return self.name

    name = models.TextField(max_length=120, unique=True)
    ref_type = models.TextField(max_length=120, default="not specified", choices=types, verbose_name="Reference type")
    description = models.TextField(max_length=360)


class Machine(models.Model):
    def __str__(self):
        return self.id_num

    client = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='machine_client',
                               related_query_name='machine_clients', blank=True, default=None, null=True)
    # TODO
    service_company = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='machine_service',
                                        related_query_name='machine_services', blank=True, default=None, null=True)
    id_num = models.TextField(max_length=30, unique=True)
    model = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='model', related_query_name='models')
    engine_model = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='engine_model',
                                     related_query_name='engine_models', )
    engine_id = models.TextField(max_length=30)
    transmission_model = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='transmission_model',
                                           related_query_name='transmission_models')
    transmission_id = models.TextField(max_length=30)
    main_bridge_model = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='main_bridge_model',
                                          related_query_name='main_bridge_models')
    main_bridge_id = models.TextField(max_length=30)
    steerable_bridge_model = models.ForeignKey(to=Reference, on_delete=models.CASCADE,
                                               related_name='steerable_bridge_model',
                                               related_query_name='steerable_bridge_models')
    steerable_bridge_id = models.TextField(max_length=30)
    supply_contract_num_date = models.TextField(max_length=120)
    shipment_date = models.DateField()
    cargo_receiver = models.TextField(max_length=120)
    supply_address = models.TextField(max_length=220)
    equipment_add = models.TextField(max_length=220)


class Maintenance(models.Model):
    def __str__(self):
        return self.order_num

    def get_machine_name(self):
        return self.machine.model

    def get_machine_id(self):
        return self.machine.id_num

    service_company = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='maintenance_ref',
                                        related_query_name='maintenance_ref', blank=True, default=None, null=True)
    mt_company = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='mt_company_ref',
                                   related_query_name='mt_companies_ref', blank=True, default=None, null=True)

    machine = models.ForeignKey(to=Machine, on_delete=models.CASCADE, related_name='maintenance_machine',
                                related_query_name='maintenance_machines')

    type = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='maintenance_type',
                             related_query_name='maintenance_types')
    mt_date = models.DateField()
    operating_time = models.TextField(max_length=120)
    order_num = models.TextField(max_length=120)
    order_date = models.DateField()


class Reclamation(models.Model):
    def __str__(self):
        return str(self.refuse_date)

    def get_downtime(self):
        delta = self.recovery_date - self.refuse_date

        return delta.days

    def get_machine_name(self):
        return self.machine.model

    def get_machine_id(self):
        return self.machine.id_num

    def save(self, *args, **kwargs):
        self.machine_downtime = self.get_downtime()
        super(Reclamation, self).save(*args, **kwargs)

    service_company = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='reclamation_ref',
                                        related_query_name='reclamations_ref', blank=True, default=None, null=True)

    machine = models.ForeignKey(to=Machine, on_delete=models.CASCADE, related_name='reclamation_machine',
                                related_query_name='reclamation_machines')

    refuse_date = models.DateTimeField()
    operating_time = models.PositiveIntegerField()
    failure_node = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='failure_node',
                                     related_query_name='failure_nodes')
    failure_description = models.TextField(max_length=220)
    recovery_method = models.ForeignKey(to=Reference, on_delete=models.CASCADE, related_name='recovery_method',
                                        related_query_name='recovery_methods')
    spare_parts_use = models.TextField(max_length=220)

    recovery_date = models.DateTimeField()
    machine_downtime = models.PositiveIntegerField(blank=True, null=True, editable=False)
