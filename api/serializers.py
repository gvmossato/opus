from rest_framework import serializers

from appsite.models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'list', 'original_id', 'name', 'done', 'creation_date', 'due_date']


    def to_representation(self, obj):
        primitive_repr = super(TaskSerializer, self).to_representation(obj)
        primitive_repr['id'] = primitive_repr.pop('id')
        primitive_repr['Subject'] = primitive_repr.pop('name')
        primitive_repr['Start_Date'] = primitive_repr['due_date']
        primitive_repr['Start_Time'] = ''
        primitive_repr['End_Date'] = primitive_repr.pop('due_date')
        primitive_repr['End_Time'] = ''
        primitive_repr['All_Day_Event'] = 'TRUE'
        primitive_repr['Description'] = ''
        primitive_repr['Location'] = ''
        primitive_repr['Private'] = 'TRUE'

        #Pops

        primitive_repr.pop('list')
        primitive_repr.pop('original_id')
        primitive_repr.pop('done')
        primitive_repr.pop('creation_date')

        return primitive_repr
