from pathlib import PosixPath as Path

import pytest
from apps.photo.exif import extract_exif_data, parse_exif_timestamp
from apps.photo.models import ImageFile
from django.core.files import File


@pytest.fixture
def jpeg_file():
    img = Path(__file__).parent / 'fixtureimage.jpg'
    assert img.exists(), 'image not found'
    return str(img)


@pytest.fixture
def img(jpeg_file):
    img = ImageFile()
    with open(jpeg_file, 'rb') as fp:
        img.source_file.save('foobar.jpg', File(fp), save=False)
    return img


@pytest.mark.django_db
def test_image_exif(img):
    assert img.exif_data == {}
    img.add_exif_from_file()

    data = extract_exif_data(img.exif_data)
    assert data.artist == 'Dennis the Dog'
    assert data.description == 'Image Description Data'
    assert data.datetime.timetuple()[:6] == (1999, 9, 9, 22, 22, 22)

    # exif data is used when image is saved
    img.save()
    assert img.created == data.datetime
    assert img.copyright_information == data.copyright
    assert img.description == data.description


@pytest.mark.django_db
def test_image_hashes(img):
    """ Save an image file and calculate hash values """
    assert img.full_width == 100
    assert img.full_height == 97
    assert img._md5 is None
    assert img._size is None
    assert img._mtime is None
    assert img._imagehash == ''
    img.calculate_hashes()
    assert img._md5[:5] == '4eccf'
    assert img._size == 2966
    assert img._mtime > 1000000000
    assert img._imagehash[:5] == '70b48'  # is string
    assert img.imagehash.hash.shape == (8, 8)  # is array
    assert img.pk is None  # did not save
    img.save()
    modified = img.modified
    assert not img.calculate_hashes()  # returns False
    assert img.modified == modified  # did not save
    img._md5 = None
    assert img.calculate_hashes()  # returns True
    assert img.modified > modified  # saved


@pytest.mark.django_db
def test_custom_field(img):
    assert img.cropping_method == img.CROP_PENDING
    assert img.crop_box.left < img.crop_box.right
    img.crop_box.right = 5
    img.crop_box.top = -5
    img.crop_box.x = 1
    img.save()
    img.refresh_from_db()
    assert img.crop_box.right == 1
    assert img.crop_box.top == 0
    assert img.crop_box.x == 1
    img.crop_box.x = -5
    img.crop_box.y = 5
    img.save()
    img.refresh_from_db()
    # put x, y inside box
    assert img.crop_box.x == img.crop_box.left
    assert img.crop_box.y == img.crop_box.bottom
