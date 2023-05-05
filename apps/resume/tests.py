from django.test import TestCase
import markdown

from .utils import FlexExtension, BoxExtension, IconExtension

# Create your tests here.

text = """
A regular paragraph of text.

::::

:::left
icon:info 男/1995.12

icon:weixin qiufengblue
:::

::: right
icon:info 男/1995.12

icon:weixin qiufengblue
:::

::::  

Another regular paragraph of text.

"""


class MarkdownTests(TestCase):
    def test_flex_extension(self):
        md = markdown.Markdown(extensions=[
            FlexExtension(),
        ])
        print(md.convert(text))

    def test_box_extension(self):
        md = markdown.Markdown(extensions=[
            BoxExtension(),
        ])
        html = md.convert(text)
        print(html)

    def test_icon_extension(self):
        md = markdown.Markdown(extensions=[
            IconExtension(),
        ])
        html = md.convert(text)
        print(html)
