from urllib.parse import unquote

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import Machine, Reference, Reclamation, Maintenance, MyUser
from .serializers import MachineSerializer, MachineRestrictedSerializer, ReferenceSerializer, ReclamationSerializer, \
    MaintenanceSerializer, MyUserSerializer, GroupSerializer, AuthenticatedSerializer, FormOptionFieldsSerializer
from rest_framework import fields


@extend_schema(tags=["Machines"])
class MachineViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset = Machine.objects.all()
    lookup_field = "id_num"
    serializer_class = MachineSerializer


@extend_schema(tags=["Machines"])
class MachineRestrictedView(RetrieveAPIView):
    authentication_classes = []
    queryset = Machine.objects.all()
    lookup_field = "id_num"
    serializer_class = MachineRestrictedSerializer


@extend_schema(tags=["References"])
class ReferenceViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    queryset = Reference.objects.all()
    lookup_field = "pk"
    lookup_value_regex = r'[\w.]+'
    serializer_class = ReferenceSerializer


ref_view = ReferenceViewSet.as_view({'get': 'retrieve'})
ref_list_view = ReferenceViewSet.as_view({'get': 'list'})


@extend_schema(tags=["maintenances"])
class MaintenanceViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer


mt_view = MaintenanceViewSet.as_view({'get': 'retrieve'})
mt_view_list = MaintenanceViewSet.as_view({'get': 'list'})


@extend_schema(tags=["Reclamations"])
class ReclamationViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer


reclamation_view = ReclamationViewSet.as_view({'get': 'retrieve'})
reclamation_view_list = ReclamationViewSet.as_view({'get': 'list'})


@extend_schema(
    description='authentication',
    request=inline_serializer(name='request_for_authentication', fields={
        'password': fields.CharField(),
        'email': fields.EmailField(),
    }),
    responses=inline_serializer(name='response_for_authentication', fields={
        'status': fields.IntegerField(), 'data': inline_serializer(
            name='user_credentials',
            fields={
                'email': fields.EmailField(),
                'password': fields.CharField(),
            }
        )
    })
)
class AuthView(APIView):
    def post(self, request):
        print(request.data)
        user = authenticate(email=request.data["email"], password=request.data["password"])
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(status=200, data={"email": user.email, 'token': token.key})
        else:
            return Response(status=401)


class ReclamationView(APIView):
    def get(self, request, id_):
        try:
            rec_object = get_object_or_404(Reclamation, id=id_)
        except Reclamation.DoesNotExist:
            raise Http404("Given query not found")

        rec_serialized = ReclamationSerializer(rec_object)
        return Response(rec_serialized.data)


class ReclamationSetView(viewsets.ReadOnlyModelViewSet):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer


@extend_schema(responses={200: MyUserSerializer})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_user(request):
    if request.method == 'GET':
        user = request.user

        groups = Group.objects.filter(user=user)
        groups_data = GroupSerializer(groups, many=True).data
        user_data = MyUserSerializer(user, context=groups).data
        user_data['groups'] = groups_data
        return Response({'user': user_data})


class AuthenticatedView(APIView):
    authentication_classes = [TokenAuthentication]

    @extend_schema(responses={200: AuthenticatedSerializer}, description='Data for authenticated users')
    def get(self, request, category='machines'):
        sorting = request.GET.get('sorting')
        try:
            user = get_object_or_404(MyUser, email=request.user)
        except MyUser.DoesNotExist:
            raise Http404("Access error")

        if user.groups.filter(name="Manager"):

            machine_list = Machine.objects.all()
            if sorting and category == 'machines':
                machine_list = machine_list.order_by(sorting)

            reclamations_list = Reclamation.objects.all()
            if sorting and category == 'reclamations':
                reclamations_list = reclamations_list.order_by(sorting)

            mt_list = Maintenance.objects.all()
            if sorting and category == 'maintenances':
                mt_list = mt_list.order_by(sorting)

            ref_list = Reference.objects.all()
            if sorting and category == 'references':
                ref_list = ref_list.order_by(sorting)

            context = {
                'client': {'name': f'Manager {user.email}'},
                'machines': MachineSerializer(machine_list, many=True).data,
                'reclamations': ReclamationSerializer(reclamations_list, many=True).data,
                'maintenances': MaintenanceSerializer(mt_list, many=True).data,
                'references': ReferenceSerializer(ref_list, many=True).data
            }
            return Response(context)

        if user.is_authenticated:
            user_ref = user.user_ref
            client_role = user.user_ref.ref_type
            user_manager = user.groups.filter(name='Manager').exists()
            print(user_ref, client_role, category)

            if client_role == 'service_company':
                if sorting and category == 'reclamations':
                    reclamations_list = Reclamation.objects.filter(service_company=user_ref)
                    reclamations_list = reclamations_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'reclamations': ReclamationSerializer(reclamations_list, many=True).data})
                if sorting and category == 'maintenances':
                    mt_list = Maintenance.objects.filter(Q(service_company=user_ref) | Q(mt_company=user_ref))
                    mt_list = mt_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'maintenances': MaintenanceSerializer(mt_list, many=True).data})
                if sorting and category == 'machines':
                    machine_list = Machine.objects.filter(service_company=user_ref)
                    machine_list = machine_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'machines': MachineSerializer(machine_list, many=True).data})

            elif client_role == 'client' or user_manager:
                machine_list = Machine.objects.filter(client=user_ref)

                if sorting and category == 'machines':
                    machine_list = machine_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'machines': MachineSerializer(machine_list, many=True).data})

                machine_ids = []
                for m in machine_list:
                    machine_ids.append(m.id_num)

                if sorting and category == 'reclamations':
                    reclamations_list = Reclamation.objects.filter(machine_id__id_num__in=machine_ids)
                    reclamations_list = reclamations_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'reclamations': ReclamationSerializer(reclamations_list, many=True).data})

                if sorting and category == 'maintenances':
                    mt_list = Maintenance.objects.filter(machine__id_num__in=machine_ids)
                    mt_list = mt_list.order_by(sorting)
                    return Response({'client': ReferenceSerializer(user_ref).data,
                                     'maintenances': MaintenanceSerializer(mt_list, many=True).data})


class CreateView(APIView):
    authentication_classes = [TokenAuthentication]

    @extend_schema(
        description='get data for form option fields depending on the permissions',
        responses={200: FormOptionFieldsSerializer()},
    )
    def get(self, request, category=None):
        # print(request.user.user_ref, request.user.user_ref.ref_type)
        user = request.user
        user_manager = user.groups.filter(name='Manager').exists()
        if not user_manager:
            user_type = user.user_ref.ref_type
            user_ref = ReferenceSerializer(user.user_ref).data
        else:
            user_type = 'Manager'
            user_ref = {'ref_type': 'Manager'}

        if category == "machine" and not user_manager:
            return Response(status=403, data={'text': 'No access'})

        if category == 'machine' and user_manager:
            ref_types = ['service_company',
                         'machine_model',
                         'engine_model',
                         'transmission_model',
                         'steerable_bridge_model',
                         'main_bridge_model',
                         'client']
            machine_ref = Reference.objects.filter(ref_type__in=ref_types)
            return Response(
                {'user_ref': user_ref,
                 'ref': ReferenceSerializer(machine_ref, many=True).data
                 }
            )
        elif category == 'maintenance':
            ref_types = ['service_company', 'maintenance_type']
            maintenance_ref = Reference.objects.filter(ref_type__in=ref_types)
            if user_type == 'client':
                machines = Machine.objects.filter(client=user.user_ref)
            if user_type == 'service_company':
                machines = Machine.objects.filter(service_company=user.user_ref)
            if user_type == 'Manager':
                machines = Machine.objects.all()
            return Response(
                {'user_ref': user_ref,
                 'ref': ReferenceSerializer(maintenance_ref, many=True).data,
                 'machines': MachineSerializer(machines, many=True).data
                 }
            )
        elif category == 'reclamation':
            ref_types = ['service_company', 'failure_node', 'recovery_method']
            reclamation_ref = Reference.objects.filter(ref_type__in=ref_types)
            if user_type == 'client':
                machines = Machine.objects.filter(client=user.user_ref)
            if user_type == 'service_company':
                machines = Machine.objects.filter(service_company=user.user_ref)
            if user_type == 'Manager':
                machines = Machine.objects.all()
            return Response(
                {'user_ref': user_ref,
                 'ref': ReferenceSerializer(reclamation_ref, many=True).data,
                 'machines': MachineSerializer(machines, many=True).data
                 }
            )
        else:
            return Response(status=400, data={'text': 'Bad request'})

    @extend_schema(
        description="receives data for adding a machine, reclamation, maintenance or reference depending "
                    "on the request parameter and user's permissions",
        request={
            'machine': MachineSerializer(),
            'reclamation': ReclamationSerializer(),
            'maintenance': MaintenanceSerializer(),
            'reference': ReferenceSerializer()
        },
        responses=inline_serializer(name='create_response', fields={'status': fields.IntegerField(default=200),
                                                                    'data': inline_serializer(
                                                                        name='status_text',
                                                                        fields={'text': fields.CharField()}
                                                                    )})

    )
    def post(self, request, category):
        user = request.user
        user_manager = user.groups.filter(name='Manager').exists()
        data = request.data
        data_new = dict(data)
        if category == 'reference':
            if user_manager:
                serializer = ReferenceSerializer(data=data_new)
                serializer.is_valid()
                print(serializer.errors)
                if serializer.is_valid():

                    serializer.save()
                    return Response(status=200, data={'text': 'Data has been added'})
                else:
                    return Response(status=400, data={'text': 'invalid data'})
            else:
                return Response(status=403, data={'text': 'No access'})

        if category == 'machine':
            if not user_manager:
                return Response(status=403, data={'text': 'No access'})
            serializer = MachineSerializer(data=data_new)
            serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                return Response(status=200, data={'text': 'Data has been added'})
            else:
                return Response(status=406, data={'text': 'invalid data'})

        if category == 'reclamation':
            serializer = ReclamationSerializer(data=data_new)
            serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                return Response(status=200, data={'text': 'Data has been added'})
            else:
                return Response(status=406, data={'text': 'invalid data'})

        if category == 'maintenance':
            serializer = MaintenanceSerializer(data=data_new)
            serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                return Response(status=200, data={'text': 'Data has been added'})
            else:
                return Response(status=406, data={'text': 'invalid data'})

    def patch(self, request, category, id):
        data = request.data
        print(category, id, data)
        user = request.user
        id_ = int(data['id'])
        data['pk'] = id_
        data.pop('id')
        user_manager = user.groups.filter(name='Manager').exists()
        print(user_manager)
        if user_manager:
            obj = None
            serializer = None
            if category == "reference":
                obj = Reference.objects.get(pk=id_)
                serializer = ReferenceSerializer(obj, data=data)
            if category == "machine":
                obj = Machine.objects.get(pk=id_)
                serializer = MachineSerializer(obj, data=data)
            if category == "maintenance":
                obj = Maintenance.objects.get(pk=id_)
                serializer = MaintenanceSerializer(obj, data=data)
            if category == "reclamation":
                obj = Reclamation.objects.get(pk=id_)
                serializer = ReclamationSerializer(obj, data=data)

            serializer.is_valid()
            print(serializer.errors)
            if serializer.is_valid():
                serializer.update(instance=obj, validated_data=serializer.validated_data)
                return Response(status=200, data={'text': 'Data has been added'})
            else:
                return Response(status=406, data={'text': 'invalid data'})
        else:
            return Response(status=403, data={'text': 'No access'})
