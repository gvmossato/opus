from rest_framework import serializers

from appsite.models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'list', 'original_id', 'name', 'done', 'date']


    def to_representation(self, obj):
        primitive_repr = super(TaskSerializer, self).to_representation(obj)
        primitive_repr['Subject'] = primitive_repr.pop('name')
        primitive_repr['Start Date'] = '12/12/2021'
        primitive_repr['Start Time'] = '12/12/2021'
        primitive_repr['End Date'] = '12/12/2021'
        primitive_repr['End Time'] = '12/12/2021'
        primitive_repr['All Day Event'] = 'TRUE'
        primitive_repr['Description'] = ''
        primitive_repr['Location'] = ''
        primitive_repr['Private'] = 'TRUE'

        #Pops

        primitive_repr.pop('id')
        primitive_repr.pop('list')
        primitive_repr.pop('original_id')
        primitive_repr.pop('done')
        primitive_repr.pop('date')

        return primitive_repr  


