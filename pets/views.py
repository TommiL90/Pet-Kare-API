from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from groups.models import Group
from pet_kare.pagination import CustomPageNumberPagination
from pets.models import Pet
from pets.serializers import PetSerializer
from traits.models import Trait
import ipdb


class PetsView(APIView, CustomPageNumberPagination):
    def post(self, request):
        # ipdb.set_trace()
        try:
            data = request.data
            serializer = PetSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            pet = serializer.data
            group_data = pet.get("group")
            # group, created = Group.objects.get_or_create(
            #     scientific_name__iexact=group_data["scientific_name"]
            # )
            try:
                group = Group.objects.get(
                    scientific_name__iexact=group_data["scientific_name"]
                )
            except Group.DoesNotExist:
                group = Group.objects.create(
                    scientific_name=group_data["scientific_name"]
                )

            trait_objects = []
            for trait_data in pet.get("traits", []):
                trait_name = trait_data["trait_name"].lower()
                try:
                    trait = Trait.objects.get(name__iexact=trait_name)
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(name=trait_name)

                trait_objects.append(trait)

            new_pet = Pet.objects.create(
                name=serializer.data["name"],
                age=serializer.data["age"],
                weight=serializer.data["weight"],
                sex=serializer.data["sex"],
                group=group,
            )
            new_pet.traits.set(trait_objects)

            return Response(PetSerializer(new_pet).data, status=201)
        except Exception:
            return Response(serializer.errors, status=400)

    def get(self, request):
        # ipdb.set_trace()
        trait = request.query_params.get(self.trait_query_param, None)
        if trait:
            pets = Pet.objects.filter(traits__name__iexact=trait)
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetsDetailsView(APIView):
    def get(self, request, pet_id):
        try:
            retrieve_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, 404)

        return Response(PetSerializer(retrieve_pet).data, status=200)

    def patch(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, 404)

        try:
            data = request.data

            serializer = PetSerializer(pet, data=data, partial=True)
            serializer.is_valid(raise_exception=True)

            pet.name = serializer.validated_data.get("name", pet.name)
            pet.sex = serializer.validated_data.get("sex", pet.sex)
            pet.weight = serializer.validated_data.get("weight", pet.weight)
            pet.age = serializer.validated_data.get("age", pet.age)

            group_data = serializer.validated_data.get("group", None)

            if group_data:
                try:
                    group = Group.objects.get(
                        scientific_name__iexact=group_data["scientific_name"]
                    )
                except Group.DoesNotExist:
                    group = Group.objects.create(
                        scientific_name=group_data["scientific_name"]
                    )
                pet.group = group

            traits_data = serializer.validated_data.get("traits", None)

            if traits_data:
                trait_objects = []
                for trait_data in traits_data:
                    trait_name = trait_data["name"].lower()
                    try:
                        trait = Trait.objects.get(name__iexact=trait_name)
                    except Trait.DoesNotExist:
                        trait = Trait.objects.create(name=trait_name)
                    trait_objects.append(trait)
                pet.traits.set(trait_objects)

            pet.save()

            return Response(PetSerializer(pet).data, status=200)

        except Exception as err:
            return Response(serializer.errors, status=400)

    def delete(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, 404)

        pet.delete()

        return Response(status=204)
