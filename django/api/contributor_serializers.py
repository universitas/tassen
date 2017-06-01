from apps.contributors.models import Contributor, Stint, Position
from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


class StintSerializer(serializers.ModelSerializer):

    """ModelSerializer for Stint"""

    class Meta:
        model = Stint
        fields = [
            'position',
            'start_date',
            'end_date',
        ]
    position = serializers.SlugRelatedField(
        read_only=True,
        slug_field='title',
    )


class ContributorSerializer(serializers.HyperlinkedModelSerializer):

    """ModelSerializer for Contributor"""

    class Meta:
        model = Contributor
        fields = [
            'url',
            'status',
            'display_name',
            'phone',
            'email',
            'byline_photo',
            'thumb',
            'verified',
            'stint_set',
        ]

    byline_photo = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='imagefile-detail'
    )
    stint_set = StintSerializer(many=True, read_only=True)
    thumb = serializers.SerializerMethodField()

    def get_thumb(self, instance):
        if not instance.byline_photo:
            return None
        build_uri = self._context['request'].build_absolute_uri
        thumbfile = instance.byline_photo.preview
        return build_uri(thumbfile.url)


class ContributorViewSet(viewsets.ModelViewSet):

    """API endpoint that allows Contributor to be viewed or updated."""

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
