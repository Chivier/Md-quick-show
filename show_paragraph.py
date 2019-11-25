#!/usr/bin/python3

import json
from typing import List

# * A Markdown-`reveal.js`-like slides look like:
# <section data-markdown >
#     <script type = "text/template" >
#       # %% [markdown] code here
#     </script>
# </section>

# todo: page seperating

SLIDE_TOPIC_BEGIN = "<section>\n"
SLIDE_TOPIC_END = "</section>\n"
SLIDE_SINGLE_BEGIN = "<section data-markdown>\n<script type=\"text/template\">\n"
SLIDE_SINGLE_END = "</script>\n</section>\n"
HEAD_NOTE_BEGIN = "<font size=\"%d\"><p style = \"text-align: left;\" > "
HEAD_NOTE_END = "</p>\n</font>"

enumerate_count = 0


def tmp_build_paragraph(js_list: List[dict]) -> str:
    str = ''
    for item in js_list:
        if item['type'] == 'text':
            str += item['value']
        elif item['type'] == 'strong':
            str += f"**{tmp_build_paragraph(item['children'])}**"
        elif item['type'] == 'emphasis':
            str += f"*{tmp_build_paragraph(item['children'])}*"
        elif item['type'] == 'delete':
            str += f"~~{tmp_build_paragraph(item['children'])}~~"
        elif item['type'] == 'image':
            str += f"![{item['alt']}]({tmp_get_link(item['url'])})"
        elif item['type'] == 'link':
            str += f"[{tmp_build_paragraph(item['children'])}]({tmp_get_link(item['url'])})"
        elif item['type'] == 'inlineCode':
            str += f"`{item['value']}`"
        else:
            print(item['type'])
            assert False
    return str


def tmp_get_link(s: str):
    return s


def print_table(f, table_to_print, indent):
    rows_of_table = table_to_print["children"]
    table_head = rows_of_table[0]
    del rows_of_table[0]

    max_length = []
    column_num = len(table_head)
    head_content = []
    align_info = table_to_print["align"]

    # f.write(align_info)

    for head_item in table_head["children"]:
        if len(head_item["children"]) == 0:
            head_item_text = "   "
        else:
            head_item_text = head_item["children"][0]["value"]
        head_content.append(head_item_text)
        max_length.append(len(head_item_text))

    # f.write(head_content)

    table_content = []

    for row_cotent in rows_of_table:
        current_row = []
        current_id = 0
        for table_cell in row_cotent["children"]:
            if len(table_cell["children"]) == 0:
                current_row.append("")
            else:
                table_cell_text = table_cell["children"][0]
                current_row.append(table_cell_text["value"])
            max_length[current_id] = max(len(current_row[current_id]),
                                         max_length[current_id])
            current_id += 1
        table_content.append(current_row)

    row_number = len(table_content)
    current_row = 0

    while current_row < row_number:
        f.write(SLIDE_SINGLE_END+"\n")
        f.write(SLIDE_SINGLE_BEGIN)

        for i in range(indent):
            f.write('    '+"")
        f.write("|"+" ")
        for current_id in range(column_num):
            f.write(head_content[current_id].ljust(
                max_length[current_id], ' ')+" | ")
        f.write("\n")

        for i in range(indent):
            f.write('    '+"")
        f.write("|"+" ")
        for current_id in range(column_num):
            alignstr = "-" * max_length[current_id]
            if align_info[current_id] == 'left':
                alignstr = ":" + "-" * (max_length[current_id] - 1)
            if align_info[current_id] == "right":
                alignstr = "-" * (max_length[current_id] - 1) + ":"
            f.write(alignstr+" | ")
        f.write("\n")

        for row_offset in range(6):
            if current_row + row_offset >= row_number:
                break
            lines = table_content[current_row + row_offset]
            for i in range(indent):
                f.write('    '+"")
            f.write("|"+" ")
            for current_id in range(column_num):
                f.write(lines[current_id].ljust(
                    max_length[current_id], ' ')+" | ")
            f.write("\n")

        current_row += 6

    f.write("\n")


def print_list(f, list_to_print, indent):
    global enumerate_count
    if enumerate_count == 6:
        f.write(SLIDE_SINGLE_END+"\n")
        f.write(SLIDE_SINGLE_BEGIN)
        enumerate_count = 0

    order_flag = list_to_print["ordered"]
    if order_flag:
        current_id = list_to_print["start"]
        for listitem in list_to_print["children"]:
            for i in range(indent):
                f.write('    ')
            f.write(str(current_id)+". ")
            current_id += 1
            enumerate_count += 1
            sublist = listitem["children"]
            print_content(f, [sublist[0]])
            del sublist[0]
            if not len(sublist) == 0:
                print_content(f, sublist, indent+1)
    else:
        for listitem in list_to_print["children"]:
            for i in range(indent):
                f.write('    '+"")
            f.write("- ")
            enumerate_count += 1
            sublist = listitem["children"]
            print_content(f, [sublist[0]])
            del sublist[0]
            if not len(sublist) == 0:
                print_content(f, sublist, indent+1)


def print_code(f, code_to_print):
    if len(code_to_print) > 1000:
        f.write(SLIDE_SINGLE_END+"\n")
        f.write(SLIDE_SINGLE_BEGIN)

    f.write("```")
    f.write(code_to_print["lang"]+"\n")
    f.write(code_to_print["value"]+"\n")
    f.write("```"+"\n")


def print_content(f, list_to_print, indent=0):
    # # check if list_to_print is a list
    # if not isinstance(list_to_print, list):
    #     list_to_print = list(list_to_print)

    common_sentence = 0
    common_paragraph = 0

    for item in list_to_print:
        # f.write(item["type"])
        # f.write(SLIDE_TOPIC_BEGIN)
        # f.write(SLIDE_SINGLE_BEGIN)
        if common_sentence > 10 or common_paragraph > 3:
            common_sentence = 0
            common_paragraph = 0
            f.write(SLIDE_SINGLE_END+"\n")
            f.write(SLIDE_SINGLE_BEGIN)

        if item["type"] == "text" or item["type"] == "html":
            for i in range(indent):
                f.write('    ')
            f.write(item["value"])
            common_sentence += 1
            continue

        if item["type"] == "thematicBreak":
            f.write(SLIDE_SINGLE_END+"\n")
            f.write(SLIDE_SINGLE_BEGIN)
            common_paragraph = 0
            continue

        if item["type"] == "link":
            alias_str = tmp_build_paragraph(item['children'])
            if alias_str == "":
                alias_str = item['url']

            f.write(
                f"[{alias_str}]({tmp_get_link(item['url'])})")
            continue

        if item["type"] == "image":
            f.write(f"![{item['alt']}]({item['url']})")
            continue

        if item["type"] == "strong":
            for i in range(indent):
                f.write('    ')
            f.write("**")
            print_content(f, item["children"], indent)
            f.write("**")
            continue

        if item["type"] == "delete":
            for i in range(indent):
                f.write('    '+"")
            f.write("~~"+"")
            print_content(f, item["children"], indent)
            f.write("~~"+"")
            continue

        if item["type"] == "emphasis":
            for i in range(indent):
                f.write('    '+"")
            f.write("_"+"")
            print_content(f, item["children"], indent)
            f.write("_"+"")
            continue

        if item["type"] == "inlineCode":
            for i in range(indent):
                f.write('    '+"")
            f.write("`"+"")
            f.write(item["value"]+"")
            f.write("`"+"")
            continue

        if item["type"] == "paragraph":
            for i in range(indent):
                f.write('    '+"")
            print_content(f, item["children"], indent)
            f.write("\n\n")
            common_paragraph += 1
            continue

        # todo: list item spreading
        if item["type"] == "list":
            print_list(f, item, indent)
            continue

        if item["type"] == "code":
            print_code(f, item)
            continue

        if item["type"] == "blockquote":
            for i in range(indent):
                f.write('    '+"")
            f.write(">"+" ")
            print_content(f, item["children"], indent)
            continue

        if item["type"] == "table":
            print_table(f, item, indent)
            continue

    # f.write(SLIDE_SINGLE_END)
    # f.write(SLIDE_TOPIC_END)
