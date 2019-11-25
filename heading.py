#!/usr/bin/python3

import os
import json
from typing import List
from show_paragraph import *

SLIDE_TOPIC_BEGIN = "<section>\n"
SLIDE_TOPIC_END = "</section>\n"
SLIDE_SINGLE_BEGIN = "<section data-markdown>\n<script type=\"text/template\">\n"
SLIDE_SINGLE_END = "</script>\n</section>\n"
HEAD_NOTE_BEGIN = "<font size=\"%d\"><p style = \"text-align: left;\" > "
HEAD_NOTE_END = "</p>\n</font>"


# * heading class
# - includes:
# - title information
# - depth information (title level)
# - subheading infoemation
# - chapter codes here
class Headings_:
    def __init__(self):
        title = []
        pure_title = []
        depth = 0
        sub_headings = []
        chapter_content = []


def readmarkdown():
    # * read markdown file
    with open('data.txt', encoding='utf-8') as json_file:
        parser = json.load(json_file)
    return parser


def build_pureparagraph(js_list: List[dict]) -> str:
    # * get a pure text for a certain paragraph
    # - Used to generate title on the left heading
    str = ''
    for item in js_list:
        if item['type'] == 'text':
            str += item['value']
        elif item['type'] == 'strong':
            str += f"{build_paragraph(item['children'])}"
        elif item['type'] == 'emphasis':
            str += f"{build_paragraph(item['children'])}"
        elif item['type'] == 'delete':
            str += f"{build_paragraph(item['children'])}~~"
        elif item['type'] == 'image':
            str += ""
        elif item['type'] == 'link':
            str += ""
        elif item['type'] == 'inlineCode':
            str += f"{item['value']}"
        else:
            print(item['type'])
            assert False
    return str


def build_paragraph(js_list: List[dict]) -> str:
    # * build paragraph with different style/fonts
    str = ''
    for item in js_list:
        if item['type'] == 'text':
            str += item['value']
        elif item['type'] == 'strong':
            str += f"**{build_paragraph(item['children'])}**"
        elif item['type'] == 'emphasis':
            str += f"*{build_paragraph(item['children'])}*"
        elif item['type'] == 'delete':
            str += f"~~{build_paragraph(item['children'])}~~"
        elif item['type'] == 'image':
            str += f"![{item['alt']}]({get_link(item['url'])})"
        elif item['type'] == 'link':
            str += f"[{build_paragraph(item['children'])}]({get_link(item['url'])})"
        elif item['type'] == 'inlineCode':
            str += f"`{item['value']}`"
        else:
            print(item['type'])
            assert False
    return str


# todo: convert file location to a local one
def get_link(s: str):
    return s


def build_headings(js: List[dict], depth: int):
    # * build heading-graph
    # show the dependencies information and such thing
    sub_headings = []
    # look for all subtitles
    index = [i for i, item in enumerate(js)
             if item['type'] == 'heading' and item['depth'] == depth]
    if len(index) == 0 and len(js) == 0:
        return [], []
    if len(index) == 0:
        return js, []
    index.append(len(js))
    for i, _ in enumerate(index[:-1]):
        choosed = js[index[i] + 1:index[i + 1]]
        sub = Headings_()
        sub.depth = depth
        sub.title = build_paragraph(js[index[i]]['children'])
        sub.pure_title = build_pureparagraph(js[index[i]]['children'])
        sub.chapter_content, sub.sub_headings = build_headings(
            choosed, depth + 1)
        sub_headings.append(sub)
    return js[:index[0]], sub_headings


def make_index(f, headinglist):
    # * print index_page
    subs = headinglist.sub_headings
    f.write("#"*2 + " ")
    f.write(headinglist.title+"\n")
    for sub in subs:
        f.write("- ")
        f.write(sub.title+"\n")


def print_markdown(f, headinglist, indexstr=""):
    id_count = 1
    for t in headinglist:
        title_show = t.pure_title

        f.write(SLIDE_TOPIC_BEGIN)
        f.write(SLIDE_SINGLE_BEGIN)
        f.write("#"*t.depth+" ")
        f.write(title_show+"\n\n")
        f.write(SLIDE_SINGLE_END)
        f.write(SLIDE_TOPIC_END)

        if len(t.sub_headings) >= 2:
            f.write(SLIDE_TOPIC_BEGIN)
            f.write(SLIDE_SINGLE_BEGIN)
            make_index(f, t)
            f.write(SLIDE_SINGLE_END)
            f.write(SLIDE_TOPIC_END)

        if len(t.chapter_content) != 0:
            f.write(SLIDE_TOPIC_BEGIN)
            f.write(HEAD_NOTE_BEGIN % (24 - t.depth*2))
            f.write(indexstr + str(id_count) + "  " + title_show)
            f.write(HEAD_NOTE_END)
            f.write(SLIDE_SINGLE_BEGIN)
            print_content(f, t.chapter_content)
            f.write(SLIDE_SINGLE_END+"\n")
            f.write(SLIDE_TOPIC_END)

        next_indexstr = indexstr + str(id_count) + "."
        print_markdown(f, t.sub_headings, next_indexstr)

        id_count += 1


def print_reveal_head():
    # * print reveal.js heading information
    head_file = open("reveal_head.txt", "r")
    head_str = head_file.read()
    fileout = open("index.html", "w")
    fileout.write(head_str)
    fileout.write("\n")
    head_file.close()
    fileout.close()


def print_reveal_tail():
    # * print reveal.js tailing information
    tail_file = open("reveal_tail.txt", "r")
    tail_str = tail_file.read()
    fileout = open("index.html", "a")
    # move cursor to the end
    fileout.seek(0, 2)
    fileout.write(tail_str)
    tail_file.close()
    fileout.close()


if __name__ == '__main__':
    print("Please input the name of Markdown:")
    filename = input("")
    print(filename)
    # filename = "tst.md"

    os.system('remark --tree-out -o data.txt ' + filename)

    with open('data.txt') as json_file:
        parser = json.load(json_file)

    print_reveal_head()

    fileout = open("index.html", "a")
    parser, sub_headings = (build_headings(parser['children'], 1))
    print_markdown(fileout, sub_headings)
    fileout.close()

    print_reveal_tail()
