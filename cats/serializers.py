import datetime as dt

import webcolors

from rest_framework import serializers
from rest_framework.response import Response

from .models import Cat, Owner, Achievement, AchievementCat


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    # owner = serializers.StringRelatedField(read_only=True)
    achievements = AchievementSerializer(many=True)
    age = serializers.SerializerMethodField()
    color = Hex2NameColor()

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements',
                  'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            return Cat.objects.create(**validated_data)
        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)
        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement)
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)
        return cat

        @action(detail=False, url_path='recent-white-cats')
        def recent_white_cats(self, request):
            cats = Cat.objects.filter(color='White')[:5]
            serializer = self.get_serializer(cats, many=True)
            return Response(serializer.data)


class OwnerSerializer(serializers.ModelSerializer):
    # cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')
