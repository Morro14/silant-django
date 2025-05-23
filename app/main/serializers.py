from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Machine, Maintenance, Reclamation, Reference, MyUser

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
choices = list(types.keys())


class ReferenceSerializer(serializers.ModelSerializer):
    ref_type = serializers.ChoiceField(choices=choices)

    def to_internal_value(self, data):
        try:
            ref = Reference.objects.get(name=data)
        except Reference.DoesNotExist:
            return super().to_internal_value(data=data)
        return ref

    def create(self, validated_data):
        ref = Reference(**validated_data)
        ref.save()
        return ref

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.ref_type = validated_data.get('ref_type', instance.ref_type)
        instance.save()
        return instance

    class Meta:
        model = Reference

        fields = "__all__"


class MachineSerializer(serializers.ModelSerializer):
    client = ReferenceSerializer()
    model = ReferenceSerializer()
    engine_model = ReferenceSerializer()
    transmission_model = ReferenceSerializer()
    main_bridge_model = ReferenceSerializer()
    steerable_bridge_model = ReferenceSerializer()
    service_company = ReferenceSerializer()
    id_num = serializers.CharField(validators=[UniqueValidator(queryset=Machine.objects.all())])

    # TODO

    # sorting_fields = serializers.SerializerMethodField()
    @extend_schema_field({'type': 'array', 'items': {'type', 'string'}})
    def get_sorting_fields(self, obj):
        sorting_fields_dict = ['model', 'engine_model', 'transmission_model', 'main_bridge_model',
                               'steerable_bridge_model', 'id_num', ]
        sorting_field = sorting_fields_dict
        return sorting_field

    def create(self, validated_data):
        machine = Machine(**validated_data)
        machine.save()
        return machine

    def to_internal_value(self, data):
        print('machine_to_internal', data)
        try:
            machine = Machine.objects.get(id_num=data)
        except Machine.DoesNotExist:
            return super().to_internal_value(data)
        return machine

    def update(self, instance, validated_data):
        instance.id_num = validated_data.get('id_num', instance.id_num)
        instance.model = validated_data.get('model', instance.model)
        instance.engine_model = validated_data.get('engine_model', instance.engine_model)
        instance.engine_id = validated_data.get('engine_id', instance.engine_id)
        instance.transmission_model = validated_data.get('transmission_model', instance.transmission_model)
        instance.transmission_id = validated_data.get('transmission_id', instance.transmission_id)
        instance.main_bridge_model = validated_data.get('main_bridge_model', instance.main_bridge_model)
        instance.main_bridge_id = validated_data.get('main_bridge_id', instance.main_bridge_id)
        instance.steerable_bridge_model = validated_data.get('steerable_bridge_model', instance.steerable_bridge_model)
        instance.main_bridge_id = validated_data.get('main_bridge_id', instance.main_bridge_id)
        instance.service_company = validated_data.get('service_company', instance.service_company)
        instance.client = validated_data.get('client', instance.client)
        instance.supply_contract_num_date = validated_data.get('supply_contract_num_date', instance.supply_contract_num_date)
        instance.shipment_date = validated_data.get('shipment_date', instance.shipment_date)
        instance.cargo_receiver = validated_data.get('cargo_receiver', instance.cargo_receiver)
        instance.supply_address = validated_data.get('supply_address', instance.supply_address)
        instance.equipment_add = validated_data.get('equipment_add', instance.equipment_add)

        instance.save()
        return instance

    class Meta:
        model = Machine

        fields = ['id',
                  'id_num',
                  'model',
                  'engine_model',
                  'engine_id',
                  'transmission_model',
                  'transmission_id',
                  'main_bridge_model',
                  'main_bridge_id',
                  'steerable_bridge_model',
                  'steerable_bridge_id',
                  'supply_contract_num_date',
                  'shipment_date',
                  'cargo_receiver',
                  'supply_address',
                  'equipment_add',
                  'client',
                  'service_company',

                  ]


class MachineRestrictedSerializer(serializers.ModelSerializer):
    # a serializer for non auth view
    model = ReferenceSerializer()
    engine_model = ReferenceSerializer()
    transmission_model = ReferenceSerializer()
    main_bridge_model = ReferenceSerializer()
    steerable_bridge_model = ReferenceSerializer()
    id_num = serializers.CharField(validators=[UniqueValidator(queryset=Machine.objects.all())])

    class Meta:
        model = Machine
        fields = ['id',
                  'id_num',
                  'model',
                  'engine_model',
                  'engine_id',
                  'transmission_model',
                  'transmission_id',
                  'main_bridge_model',
                  'main_bridge_id',
                  'steerable_bridge_model',
                  'steerable_bridge_id',
                  ]


class ReclamationSerializer(serializers.ModelSerializer):
    failure_node = ReferenceSerializer()
    recovery_method = ReferenceSerializer()
    service_company = ReferenceSerializer()
    machine = MachineSerializer()
    # machine_downtime = serializers.CharField(source="get_downtime", read_only=True)
    refuse_date = serializers.DateTimeField()
    recovery_date = serializers.DateTimeField()

    def create(self, validated_data):
        rec = Reclamation(**validated_data)
        rec.save()
        return rec

    class Meta:
        model = Reclamation

        fields = [
            'id',
            'refuse_date',
            'operating_time',
            'failure_node',
            'failure_description',
            'recovery_method',
            'spare_parts_use',
            'recovery_date',
            'machine_downtime',
            'machine',
            'service_company'
        ]


class MaintenanceSerializer(serializers.ModelSerializer):
    type = ReferenceSerializer()

    machine = MachineSerializer()
    service_company = ReferenceSerializer()
    mt_company = ReferenceSerializer()

    class Meta:
        model = Maintenance

        fields = [
            'id',
            'type',
            'mt_date',
            'operating_time',
            'order_num',
            'order_date',
            'machine',
            'service_company',
            'mt_company',

        ]


class GroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Group
        fields = ['name']


class DateSerializer(serializers.Serializer):
    date = serializers.DateField()


class DateTimeSerializer(serializers.Serializer):
    date = serializers.DateTimeField()


class MyUserSerializer(serializers.ModelSerializer):
    user_ref = serializers.SlugRelatedField(slug_field="name", queryset=Reference.objects.all())

    class Meta:
        model = MyUser
        fields = ['email', 'user_type', 'user_ref']


class AuthenticatedSerializer(serializers.Serializer):
    client = serializers.CharField()
    machines = MachineSerializer(many=True)
    reclamations = ReclamationSerializer(many=True)
    maintenances = MaintenanceSerializer(many=True)
    references = ReferenceSerializer(many=True)


class FormOptionFieldsSerializer(serializers.Serializer):
    user_ref = ReferenceSerializer()
    ref = ReferenceSerializer(many=True)
    machines = MachineSerializer(many=True)
