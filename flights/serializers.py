from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Flight, Booking, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):

	flight = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='destination'
     )

	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
	total = serializers.SerializerMethodField()
	flight = FlightSerializer()

	class Meta:
		model = Booking
		fields = ['flight', 'date', 'passengers', 'id', 'total']

	def get_total(self, obj):
		total_obj = obj.flight.price * obj.passengers
		return total_obj


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data


class ProfileSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	past_bookings = serializers.SerializerMethodField()
	tier = serializers.SerializerMethodField()

	class Meta:
		model = Profile
		fields = ['user', 'miles','past_bookings','tier']

	def get_past_bookings(self, obj):
		past_bookings_objs = obj.user.bookings.filter(date__lt=timezone.now())
		past_bookings_json = BookingSerializer(past_bookings_objs, many=True).data
		return past_bookings_json 

	def get_tier(self, obj):
		if obj.miles >= 0 and obj.miles <= 9999:
			tier = 'Blue'
			return tier
		elif obj.miles >= 10000 and obj.miles <= 59999:
			tier = 'Silver'
			return tier
		elif obj.miles >= 60000 and obj.miles <= 99999:
			tier = 'Gold'
			return tier
		elif obj.miles >= 100000:
			tier = 'Platinum'
			return tier

