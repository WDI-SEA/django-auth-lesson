from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token

from ..models.mango import Mango
from ..serializers import MangoSerializer

# Create your views here.
class Mangos(generics.ListCreateAPIView):
    def get(self, request):
        """Index request"""
        mangos = Mango.objects.all()
        data = MangoSerializer(mangos, many=True).data
        return Response(data)

    serializer_class = MangoSerializer
    def post(self, request):
        """Create request"""
        # Serialize/create mango
        mango = MangoSerializer(data=request.data['mango'])
        if mango.is_valid():
            m = mango.save()
            return Response(mango.data, status=status.HTTP_201_CREATED)
        else:
            return Response(mango.errors, status=status.HTTP_400_BAD_REQUEST)

class MangoDetail(generics.RetrieveUpdateDestroyAPIView):
    def get(self, request, pk):
        """Show request"""
        mango = get_object_or_404(Mango, pk=pk)
        data = MangoSerializer(mango).data
        return Response(data)

    def delete(self, request, pk):
        """Delete request"""
        mango = get_object_or_404(Mango, pk=pk)
        mango.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        mango = get_object_or_404(Mango, pk=pk)
        # Validate updates with serializer
        ms = MangoSerializer(mango, data=request.data['mango'])
        if ms.is_valid():
            ms.save()
            return Response(ms.data)
        return Response(ms.errors, status=status.HTTP_400_BAD_REQUEST)
