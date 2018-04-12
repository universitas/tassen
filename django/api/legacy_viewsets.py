import json
import logging

from apps.photo.models import ImageFile
from apps.stories.models import Story, StoryImage, StoryType
from rest_framework import authentication, serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from url_filter.integrations.drf import DjangoFilterBackend

logger = logging.getLogger('apps')


class MissingImageFileException(Exception):
    pass


class ProdBildeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryImage
        fields = [
            'prodbilde_id',
            'bildefil',
            'prioritet',
            'bildetekst',
        ]

    prodbilde_id = serializers.IntegerField(source='id', required=False)
    bildefil = serializers.CharField(source='filename')
    prioritet = serializers.IntegerField(source='size', required=False)
    bildetekst = serializers.CharField(source='caption')


def get_imagefile(filename):
    img = ImageFile.objects.filter(original__endswith=filename).last()
    if img is None:
        raise MissingImageFileException('ImageFile("%s") not found' % filename)
    return img


def update_images(images, story):
    for img_data in images:
        pk = img_data.get('prodbilde_id', 0)
        logger.debug(json.dumps(img_data))
        try:
            if pk:
                update_story_image(story, pk, **img_data)
            else:
                create_story_image(story, **img_data)
        except MissingImageFileException as err:
            logger.warn(f'ignore missing image {err}')


def update_story_image(
    story, pk, bildefil=None, prioritet=None, bildetekst=None, **kwargs
):
    try:
        story_image = StoryImage.objects.get(pk=pk, parent_story=story)
    except StoryImage.DoesNotExist:
        story_image = StoryImage(parent_story=story)
    if bildefil and bildefil != story_image.filename:
        story_image.image_file = get_imagefile(bildefil)
    if prioritet is not None:
        story_image.size = prioritet
    if bildetekst is not None:
        story_image.caption = bildetekst
    try:
        story_image.save()
    except Exception:
        logger.exception('could not save image')

    return story_image


def create_story_image(story, bildefil, prioritet=0, bildetekst='', **kwargs):
    image_file = get_imagefile(bildefil)
    return StoryImage.objects.create(
        parent_story=story,
        imagefile=image_file,
        size=prioritet,
        caption=bildetekst,
    )


class ProdStorySerializer(serializers.ModelSerializer):
    """ModelSerializer for Story based on legacy prodsys"""

    class Meta:
        model = Story
        fields = [
            'bilete',
            'prodsak_id',
            'mappe',
            'arbeidstittel',
            'produsert',
            'tekst',
            'url',
            'version_no',
        ]
        extra_kwargs = {'url': {'view_name': 'legacy-detail'}}

    bilete = ProdBildeSerializer(required=False, many=True, source='images')
    prodsak_id = serializers.IntegerField(source='id', required=False)
    mappe = serializers.SerializerMethodField()
    arbeidstittel = serializers.CharField(source='working_title')
    produsert = serializers.IntegerField(source='publication_status')
    tekst = serializers.CharField(style={'base_template': 'textarea.html'})
    version_no = serializers.SerializerMethodField()

    def _build_uri(self, url):
        return self._context['request'].build_absolute_uri(url)

    def get_mappe(self, instance):
        return instance.story_type.prodsys_mappe

    def get_version_no(self, instance):
        return 1

    def to_internal_value(self, data):
        out = super().to_internal_value(data)
        out['images'] = data.get('bilete', [])
        mappe = data.get('mappe')
        if mappe:
            out['story_type'] = StoryType.objects.filter(
                prodsys_mappe=mappe
            ).first() or StoryType.objects.first()
        return out

    def create(self, validated_data):
        bilete = validated_data.pop('images', [])
        if Story.objects.filter(pk=validated_data.get('id')):
            raise ValidationError('Story exists')
        story = super().create(validated_data)
        update_images(bilete, story)
        return story

    def update(self, instance, validated_data):
        bilete = validated_data.pop('images', [])
        story = super().update(instance, validated_data)
        update_images(bilete, story)
        story.full_clean()
        story.save()
        return story


class UnicodeJSONRenderer(JSONRenderer):
    ensure_ascii = True


class ProdStoryViewSet(viewsets.ModelViewSet):

    renderer_classes = (UnicodeJSONRenderer, BrowsableAPIRenderer)
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    )
    # permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    serializer_class = ProdStorySerializer
    queryset = Story.objects.order_by('publication_status', 'modified').filter(
        publication_status__lt=Story.STATUS_PUBLISHED,
    ).prefetch_related(
        'story_type',
        'bylines',
        'byline_set',
        'images',
    )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['publication_status', 'title', 'bodytext_markup']