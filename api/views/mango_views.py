from rest_framework.views import APIView
from rest_framework.response import Response
# if we wanted to only protect a few resources, we'd change default permission_classes in our settings, and pass the IsAuthenticated like we see in the comment at the top of the Mangos view for index and create
# from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token

from ..models.mango import Mango
from ..serializers import MangoSerializer

# Create your views here.
class Mangos(generics.ListCreateAPIView):
    # See here in ref to comment at the top
    # permission_classes=(IsAuthenticated,)
    def get(self, request):
        print(request.user)
        """Index request"""
        # 1. query for all the mangos --> here we use .all()
        # mangos = Mango.objects.all()
        # what we want to do is use filter() to only send back the mangos owned by the user
        mangos = Mango.objects.filter(owner=request.user.id)
        # 2. Serializer --> formats the data we just found
        data = MangoSerializer(mangos, many=True).data
        # 3. return a response
        return Response(data)

    serializer_class = MangoSerializer
    def post(self, request):
        """Create request"""
        # The currently signed-in user
        print(request.user)

        # 1. Set up our new mango data
        # the data we're expecting to receive looks like this:
        # { 'mango': {'name': 'larry the mango', 'ripe': true, 'color':'green'}}
        # make the mango_data dictionary out of the request data so we can add to it
        mango_data = request.data['mango']
        mango_user = request.user.id
        # to manage the ownership of this mango, we'll check out our dictionary to make sure it looks right, and to make sure it is in fact a dictionary
        print(mango_data)
        print(type(mango_data))

        # now, we'll use square bracket syntax to access the k:v pairs
        # as well as add the owner
        mango_data['owner'] = mango_user

        # if we wanted to do this all in one line, it would look like this
        # request.data['mango']['owner'] = request.user.id

        # now, we need to run everything through the serializer
        # Serialize/create mango
        # mango = MangoSerializer(data=request.data['mango'])
        mango = MangoSerializer(data=mango_data)
        if mango.is_valid():
            m = mango.save()
            return Response(mango.data, status=status.HTTP_201_CREATED)
        else:
            return Response(mango.errors, status=status.HTTP_400_BAD_REQUEST)

class MangoDetail(generics.RetrieveUpdateDestroyAPIView):
    def get(self, request, pk):
        """Show request"""
        # 1. query for our resource(the mango)
        mango = get_object_or_404(Mango, pk=pk)
        print(mango.owner)
        # 1a. Throw an error if the user making the request is not the owner
        # rest framework has an error called `PermissionDenied`
        if request.user != mango.owner:
            raise PermissionDenied('You do not own this mango.')
        # 2. format our mango with the Serializer
        data = MangoSerializer(mango).data
        # 3. return our response
        return Response(data)

    def delete(self, request, pk):
        """Delete request"""
        # we query of course
        mango = get_object_or_404(Mango, pk=pk)
        # permission check
        if request.user != mango.owner:
            raise PermissionDenied('Cant delete a mango you dont own bub')
        # delete
        mango.delete()
        # return a response
        return Response(status=status.HTTP_204_NO_CONTENT)

    # partial update allows missing data on the incoming request
    # this is based on our serializer rules
    # this is a patch request complete with owner protection
    def partial_update(self, request, pk):
        """Update Request"""
        # 1. Query, find the mango we want to update
        mango = get_object_or_404(Mango, pk=pk)
        # 1a. Permissions check - do they own it
        if request.user != mango.owner:
            # here we raise permission denied again
            raise PermissionDenied('Cant update a mango you dont own bub')
        
        # 2. we want to override the owner field on the incoming data
        # this will prevent people from changing the owner, since in this api
        # the owner should always be the same.
        mango_data = request.data['mango']
        mango_data['owner'] = request.user.id

        # 3. Serializer needs updated, so we provide the current mango
        # tell it to use partial updates if needed
        # and tell it which mango to update
        # Validate updates with serializer
        # ms = MangoSerializer(mango, data=request.data['mango'])
        ms = MangoSerializer(mango, data=mango_data, partial=True)
        # we are validating the changes
        if ms.is_valid():
            # if the change is valid, save it
            ms.save()
            # return a response with data
            return Response(ms.data)
        # return a response if there are any errors
        return Response(ms.errors, status=status.HTTP_400_BAD_REQUEST)
