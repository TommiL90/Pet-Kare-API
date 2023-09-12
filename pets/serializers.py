from rest_framework import serializers
from groups.models import Group
from groups.serializers import GroupSerializer
from pets.models import SexChoices
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=SexChoices.choices,
        allow_blank=True,
        default=SexChoices.NOT_INFORMED
    )
    group = GroupSerializer()
    traits = TraitSerializer(many=True)

    # def update(self, instance, validated_data):
    #     instance.id = validated_data.get('id', instance.id)
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.sex = validated_data.get('sex', instance.sex)
    #     instance.weight = validated_data.get('weight', instance.weight)
    #     instance.age = validated_data.get('age', instance.age)
    #     instance.group = validated_data.get('group', instance.group)
    #     instance.traits.set(validated_data.get('traits', instance.traits.all()))
    #     instance.save()
    #     return instance
