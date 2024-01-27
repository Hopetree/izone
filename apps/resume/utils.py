import re

from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree


class FlexBlockProcessor(BlockProcessor):
    RE_FENCE_START = r'\n*:{4,}\s*\n*'
    RE_FENCE_END = r'\n*:{4,}\s*$'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            # print(re.search(self.RE_FENCE_END, block), block)
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                # render fenced area inside a new div
                e = etree.SubElement(parent, 'div')
                e.set('class', 'flex-container')
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class BoxBlockProcessor(BlockProcessor):
    RE_FENCE_START = r'^:{3}\s*left\n*|^:{3}\s*right\n*'  # start line, e.g., `   !!!! `
    RE_FENCE_END = r'\n*:{3}$'  # last non-blank line, e.g, '!!!\n  \n\n'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        # print(blocks)
        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            # print(re.search(self.RE_FENCE_END, block), block)
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                # render fenced area inside a new div
                e = etree.SubElement(parent, 'div')
                if 'left' in original_block:
                    e.set('class', 'left')
                elif 'right' in original_block:
                    e.set('class', 'right')
                else:
                    return False
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class IconInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        text = m.group(1)
        el = etree.Element('i')
        el.set('class', 'fa fa-{}'.format(text.replace('icon:', '')))
        return el, m.start(0), m.end(0)


class FlexExtension(Extension):
    """
    生成flex的div
    """

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(FlexBlockProcessor(md.parser), 'flex', 198)


class BoxExtension(Extension):
    """
    生成左右对齐的div
    """

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(BoxBlockProcessor(md.parser), 'box', 199)


class IconExtension(Extension):
    """
    渲染图标
    """

    def extendMarkdown(self, md):
        DEL_PATTERN = r'(icon:[a-z-]+)'
        md.inlinePatterns.register(IconInlineProcessor(DEL_PATTERN, md), 'icon', 200)
