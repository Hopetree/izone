import re

from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree


class DelInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('del')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class DelExtension(Extension):
    """
    删除文本
    匹配：~~删除~~
    输出：<del>删除</del>
    """

    def extendMarkdown(self, md):
        DEL_PATTERN = r'~~(.*?)~~'  # like ~~del~~
        md.inlinePatterns.register(DelInlineProcessor(DEL_PATTERN, md), 'del', 180)


class IconInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        text = m.group(1)
        el = etree.Element('i')
        el.set('class', 'fa fa-{}'.format(text.replace('icon:', '')))
        return el, m.start(0), m.end(0)


class IconExtension(Extension):
    """
    渲染图标
    匹配：icon:exclamation-triangle
    输出：<i class="fa fa-exclamation-triangle"></i>
    """

    def extendMarkdown(self, md):
        DEL_PATTERN = r'(icon:[a-z-]+)'
        md.inlinePatterns.register(IconInlineProcessor(DEL_PATTERN, md), 'icon', 179)


class AlertBlockProcessor(BlockProcessor):
    RE_FENCE_START = r'^:{3}\s*primary\s*.*\n*|^:{3}\s*secondary\s*.*\n*|^:{3}\s*success\s*.*\n*|^:{3}\s*danger\s*.*\n*|^:{3}\s*warning\s*.*\n*|^:{3}\s*info\s*.*\n*'
    RE_FENCE_END = r'\n*:{3}$'

    icon_dict = {
        'primary': 'info-circle',
        'secondary': 'info-circle',
        'success': 'info-circle',
        'danger': 'warning',
        'warning': 'warning',
        'info': 'info-circle'
    }

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        # print(blocks)
        original_block = blocks[0]
        first_blocks = original_block.split()
        if len(first_blocks) == 3:
            title = first_blocks[2]
        elif len(first_blocks) == 2:
            title = 'Tip'
        else:
            return False
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])
        # print(blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            # print(re.search(self.RE_FENCE_END, block), block)
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                # render fenced area inside a new div
                e = etree.SubElement(parent, 'div')
                icon_elm = etree.Element('i')
                strong_tag = etree.Element('strong')
                title_elm = etree.Element('p')
                class_value = 'alert alert-{}'
                flag = False
                for key in ['primary', 'secondary', 'success', 'danger', 'warning', 'info']:
                    if key in original_block:
                        e.set('class', class_value.format(key))
                        e.set('role', 'alert')
                        icon_elm.set('class', 'fa fa-{}'.format(self.icon_dict[key]))
                        strong_tag.append(icon_elm)
                        span_elm = etree.Element('span')
                        span_elm.text = title
                        strong_tag.append(span_elm)
                        title_elm.append(strong_tag)
                        e.insert(0, title_elm)
                        flag = True
                        break
                if not flag:
                    return False
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class AlertExtension(Extension):
    """
    生产Alert块
    """

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(AlertBlockProcessor(md.parser), 'alert', 178)


if __name__ == '__main__':
    import markdown

    m = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        DelExtension(),
        IconExtension(),
        AlertExtension()
    ])

    t = '''
::: warning 提示

注意，这是一个演示效果，~~我是被删除的内容~~
:::
    '''

    html = m.convert(t)
    print(html)
