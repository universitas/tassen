# -*- coding: utf-8 -*-
""" Content in the publication. """

# Python standard library
# import subprocess
import re
import datetime
from io import BytesIO
import logging

# Django core
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.files.base import ContentFile
# from django.utils.text import slugify

# Installed apps
import PyPDF2
from sorl.thumbnail import ImageField
from wand.image import Image as WandImage
from wand.color import Color
# from wand.exceptions import BlobError
from wand.drawing import Drawing
import os.path
# Project apps

from utils.model_mixins import Edit_url_mixin
logger = logging.getLogger('universitas')


def pdf_not_found(pdf_name):
    """Creates an error frontpage"""
    img = WandImage(
        width=300,
        height=500,
    )
    msg = 'ERROR:\n{}\nnot found on disk'.format(pdf_name)
    with Drawing() as draw:
        #draw.font = 'wandtests/assets/League_Gothic.otf'
        #draw.font_size = 40
        draw.text_alignment = 'center'
        draw.text(img.width // 2, img.height // 3, msg)
        draw(img)
    return img


def current_issue():
    """ Return a tuple of year and number for the current issue. """
    today = timezone.now().astimezone().date()
    latest_issue = Issue.objects.latest_issue()
    if latest_issue.publication_date == today:
        current_issue = latest_issue
    else:
        current_issue = Issue.objects.next_issue()

    return (current_issue.year, current_issue.number)


class IssueQueryset(models.QuerySet):

    def published(self):
        query = self.filter(publication_date__lte=timezone.now())
        return query

    def unpublished(self):
        query = self.filter(publication_date__gt=timezone.now())
        return query

    def next_issue(self):
        return self.unpublished().last()

    def latest_issue(self):
        return self.published().first()


class Issue(models.Model, Edit_url_mixin):

    """ Past or future print issue """

    objects = IssueQueryset.as_manager()

    REGULAR = 1
    MAGAZINE = 2
    SPECIAL = 3

    ISSUE_TYPES = [
        (REGULAR, _('Regular')),
        (MAGAZINE, _('Magazine')),
        (SPECIAL, _('Welcome special')),
    ]

    publication_date = models.DateField(blank=True, null=True)
    issue_type = models.PositiveSmallIntegerField(
        choices=ISSUE_TYPES,
        default=REGULAR)

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return self.issue_name

    def natural_key(self):
        return '{}'.format(self.publication_date)

    @property
    def number(self):

        issue_list = Issue.objects.filter(
            publication_date__year=self.year
        ).order_by('publication_date').values_list(
            'id',
            flat=True,
        )

        return list(issue_list).index(self.id) + 1

    @property
    def advert_deadline(self):
        two_days = datetime.timedelta(days=2)
        return self.publication_date - two_days

    @property
    def year(self):
        return self.publication_date.year

    @property
    def issue_name(self):
        if self.issue_type == Issue.REGULAR:
            description = ''
        else:
            description = ' ({})'.format(
                self.get_issue_type_display()
            )
        name = '{number}/{year}{desc} {pub_date:%d. %b}'.format(
            year=self.year,
            number=self.number,
            desc=description,
            pub_date=self.publication_date,
        )
        return name


class PrintIssue(models.Model, Edit_url_mixin):

    """ PDF file of a printed newspaper. """

    class Meta:
        # ordering = ['-publication_date']
        verbose_name = _('Pdf issue')
        verbose_name_plural = _('Pdf issues')

    issue = models.ForeignKey(Issue, null=True, related_name='pdfs')

    # publication_date = models.DateField(blank=True, null=True)

    pages = models.IntegerField(
        help_text='Number of pages',
        editable=False,)

    pdf = models.FileField(
        help_text=_('Pdf file for this issue.'),
        upload_to='pdf/',
        blank=True, null=True,
    )

    cover_page = ImageField(
        help_text=_('An image file of the front page'),
        upload_to='pdf/covers/',
        blank=True,
        null=True,
    )

    text = models.TextField(
        help_text=_('Extracted from file.'),
        editable=False,
    )

    def __str__(self):
        return self.pdf.url

    def save(self, *args, **kwargs):
        if self.pk:
            old_self = type(self).objects.get(pk=self.pk)
        else:
            old_self = PrintIssue()
        if self.pdf and old_self.pdf != self.pdf:
            reader = PyPDF2.PdfFileReader(self.pdf)
            self.pages = reader.numPages
            self.text = reader.getPage(0).extractText()[:200]
            self.cover_page.delete()
        if not self.pdf and self.cover_page:
            self.cover_page.delete()
        if self.pdf and not self.issue:
            publication_date = self.get_publication_date()
            self.issue, created = Issue.objects.get_or_create(
                publication_date=publication_date,
            )

        super().save(*args, **kwargs)

        def cover_as_image(self):

            def pdf_frontpage_to_image():
                reader = PyPDF2.PdfFileReader(self.pdf.file)
                writer = PyPDF2.PdfFileWriter()
                writer.addPage(reader.getPage(0))
                outputStream = BytesIO()
                writer.write(outputStream)
                outputStream.seek(0)
                img = WandImage(
                    blob=outputStream,
                    format='pdf',
                    resolution=60)
                return img

            def pdf_not_found():
                """Creates an error frontpage"""
                img = WandImage(width=400, height=600,)
                msg = 'ERROR:\n{}\nnot found on disk'.format(self.pdf.name)
                with Drawing() as draw:
                    #draw.font = 'wandtests/assets/League_Gothic.otf'
                    #draw.font_size = 40
                    draw.text_alignment = 'center'
                    draw.text(img.width // 2, img.height // 3, msg)
                    draw(img)
                return img

            try:
                return pdf_frontpage_to_image()
            except Exception as e:
                raise

    def create_thumbnail(self):
        """ Create a jpg version of the pdf frontpage """

        def pdf_frontpage_to_image():
            reader = PyPDF2.PdfFileReader(self.pdf.file)
            writer = PyPDF2.PdfFileWriter()
            writer.addPage(reader.getPage(0))
            outputStream = BytesIO()
            writer.write(outputStream)
            outputStream.seek(0)
            img = WandImage(
                blob=outputStream,
                format='pdf',
                resolution=60)
            return img

        def pdf_not_found():
            """Creates an error frontpage"""
            img = WandImage(width=400, height=600,)
            msg = 'ERROR:\n{}\nnot found on disk'.format(self.pdf.name)
            with Drawing() as draw:
                #draw.font = 'wandtests/assets/League_Gothic.otf'
                #draw.font_size = 40
                draw.text_alignment = 'center'
                draw.text(img.width // 2, img.height // 3, msg)
                draw(img)
            return img

        filename = self.pdf.name.replace(
            '.pdf', '.jpg').replace(
            'pdf/', 'pdf/covers/')

        try:
            cover = pdf_frontpage_to_image()
        except Exception as ex:
            cover = pdf_not_found()
            filename = filename.replace('.jpg', '_not_found.jpg')
            logger.warn('pdf not found: %s' % self.pdf.name )

        background = WandImage(
            width=cover.width,
            height=cover.height,
            background=Color('white'))
        background.format = 'jpeg'
        background.composite(cover, 0, 0)
        blob = BytesIO()
        background.save(blob)
        imagefile = ContentFile(blob.getvalue())

        self.cover_page.save(filename, imagefile, save=True)

    def get_thumbnail(self):
        """ Get or create a jpg version of the pdf frontpage """
        pdf = self.pdf
        if not pdf:
            return None
        if self.cover_page:
            return self.cover_page
            # There is a cover thumb
            # timestamp = os.path.getmtime
            # if timestamp(cover.path) > timestamp(pdf.path):
            # Pdf has not changed
            #     return self.cover_page
            # else:
            #     self.cover_page.delete()

        self.create_thumbnail()
        return self.cover_page

    def extract_page_text(self, page_number):
        """ Extracts text from a page in the pdf """
        pdf_file = PyPDF2.PdfFileReader(self.pdf, strict=True)
        text = pdf_file.getPage(page_number - 1).extractText()
        return text

    def get_publication_date(self):
        page_2_text = self.extract_page_text(2)
        dateline_regex = r'^\d(?P<day>\w+) (?P<date>\d{1,2})\. (?P<month>\w+) (?P<year>\d{4})'
        MONTHS = [
            'januar', 'februar', 'mars', 'april', 'mai', 'juni',
            'juli', 'august', 'september', 'oktober', 'november', 'desember',
        ]
        dateline = re.match(dateline_regex, page_2_text)
        if dateline:
            day = int(dateline.group('date'))
            year = int(dateline.group('year'))
            month = MONTHS.index(dateline.group('month')) + 1
            created = datetime.date(day=day, month=month, year=year)
        else:
            # Finds creation date.
            created = datetime.date.fromtimestamp(
                os.path.getmtime(self.pdf.path))
            # Sets creation date as a Wednesday, if needed.
            created = created + datetime.timedelta(
                days=3 - created.isoweekday())
        return created

    # @models.permalink
    def get_absolute_url(self):
        return self.pdf.url


@receiver(pre_delete, sender=PrintIssue)
def delete_pdf_and_cover_page(sender, instance, **kwargs):
    instance.cover_page.delete(False)
    instance.pdf.delete(False)
