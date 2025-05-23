import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Reference, Machine, Reclamation, Maintenance, MyUser

datetime_formats = settings.DATETIME_INPUT_FORMATS

datetime_formats_str = 'Formats: '
for f in datetime_formats:

    datetime_formats_str += (f + ' | ')

date_formats = settings.DATE_INPUT_FORMATS
date_formats_str = 'Formats: '
for f in date_formats:

    date_formats_str += (f + ' | ')


class MyUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_ref_query = Reference.objects.filter(ref_type='service_company') | Reference.objects.filter(ref_type='client')
        self.fields['user_ref'].queryset = user_ref_query

    class Meta:
        model = MyUser
        fields = ['email',
                  'user_type',
                  'user_ref']


class MyUserChangenForm(UserChangeForm):
    user_ref = Reference.objects.filter(ref_type='service_company') | Reference.objects.filter(ref_type='client')

    class Meta:
        model = MyUser
        fields = ['email',
                  'user_type',
                  'user_ref']


class ReferenceForm(forms.ModelForm):
    class Meta:
        fields = '__all__'


class MachineModelForm(forms.ModelForm):
    shipment_date = forms.DateField(help_text=date_formats_str)
    id_num = forms.CharField(label='Serial number')
    engine_id = forms.CharField(label='Engine serial number')
    transmission_id = forms.CharField(label='Transmission serial number')
    steerable_bridge_id = forms.CharField(label=' Steerable bridge serial number')
    main_bridge_id = forms.CharField(label='Main bridge serial number')

    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        service_ref_query = Reference.objects.filter(ref_type='service_company')
        client_ref_query = Reference.objects.filter(ref_type='client')
        machine_ref_query = Reference.objects.filter(ref_type='machine_model')
        engine_ref_query = Reference.objects.filter(ref_type='engine_model')
        transmission_ref_query = Reference.objects.filter(ref_type='transmission_model')
        main_bridge_ref_query = Reference.objects.filter(ref_type='main_bridge_model')
        steering_bridge_ref_query = Reference.objects.filter(ref_type='steerable_bridge_model')
        self.fields['service_company'].queryset = service_ref_query
        self.fields['client'].queryset = client_ref_query
        self.fields['model'].queryset = machine_ref_query
        self.fields['engine_model'].queryset = engine_ref_query
        self.fields['transmission_model'].queryset = transmission_ref_query
        self.fields['main_bridge_model'].queryset = main_bridge_ref_query
        self.fields['steerable_bridge_model'].queryset = steering_bridge_ref_query


class ReclamationModelForm(forms.ModelForm):
    refuse_date = forms.DateTimeField(label='Refuse date and time', help_text=datetime_formats_str)
    recovery_date = forms.DateTimeField(label='Recovery date and time', help_text=datetime_formats_str)
    operating_time = forms.CharField(label='Operating time, m/h')

    class Meta:
        model = Reclamation
        exclude = ('machine_downtime',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        failure_node = Reference.objects.filter(ref_type='failure_node')
        recovery_method = Reference.objects.filter(ref_type='recovery_method')
        service_company = Reference.objects.filter(ref_type='service_company')

        self.fields['failure_node'].queryset = failure_node
        self.fields['recovery_method'].queryset = recovery_method
        self.fields['service_company'].queryset = service_company


class MaintenanceModelForm(forms.ModelForm):
    mt_date = forms.DateField(label='Maintenance date', help_text=date_formats_str)
    order_date = forms.DateField(label='Oder date', help_text=date_formats_str)

    class Meta:
        model = Maintenance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type = Reference.objects.filter(ref_type='maintenance_type')
        service_company = Reference.objects.filter(ref_type='service_company')
        mt_company = Reference.objects.filter(ref_type='service_company')

        self.fields['type'].queryset = type
        self.fields['service_company'].queryset = service_company
        self.fields['mt_company'].queryset = mt_company
        self.fields['mt_company'].label = 'Maintenance company'
