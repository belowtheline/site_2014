# -*- coding: utf-8 -*-

import cPickle
import cStringIO
import functools
import os
import string

from flask import Flask, abort, make_response, request

from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import rollbar

app = Flask(__name__)

DISCLAIMER_TEXT = "This is a custom-generated voting reference not under " \
                  "any circumstances to be distributed or used as how to " \
                  "vote material.  For more information please visit " \
                  "http://belowtheline.org.au/"
LOGO_FILENAME = 'belowtheline-print.png'

STATES = {
    'act': 'Australian Capital Territory',
    'nsw': 'New South Wales',
    'nt': 'Northern Territory',
    'qld': 'Queensland',
    'sa': 'South Australia',
    'tas': 'Tasmania',
    'vic': 'Victoria',
    'wa': 'Western Australia',
}

DIVISION_TEXT = "Your ballot for {} is to the left."
STATE_TEXT = "Your ballot for {} is to the right."

FONT = 'Helvetica'
A4R = landscape(A4)

PAGE_HEIGHT = A4R[1]
PAGE_WIDTH = A4R[0]

TOP_MARGIN = 10 * mm
BOTTOM_MARGIN = 6.5 * mm
LEFT_MARGIN = 6.5 * mm
RIGHT_MARGIN = 6.5 * mm

GROUP_ROW_GAP = 5 * mm

BOX_SIZE = 6 * mm
DIVISION_BOX_GAP = 5.5 * mm
BOX_GAP = 7 * mm

FONT_SIZE = 8.0
CANDIDATE_FONT_SIZE = 7.5
PARTY_FONT_SIZE = 5.0

GROUPS_PER_ROW = 8

GROUP_WIDTH = (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN) / GROUPS_PER_ROW
LABEL_WIDTH = GROUP_WIDTH - BOX_SIZE - 6 * mm

ballots = cPickle.load(open('ballots.pck'))

def disclaimer(c):
    c.drawString(10 * mm, PAGE_HEIGHT - 6 * mm, DISCLAIMER_TEXT)

def watermark(c):
    c.saveState()
    c.setStrokeColorRGB(0.93333, 0.93333, 0.93333)
    c.setFillColorRGB(0.93333, 0.93333, 0.93333)
    c.setFont(FONT, 90.0)
    c.rotate(35.3)
    c.drawString(40 * mm, 0, "belowtheline.org.au")
    c.restoreState()

def end_page(c):
    disclaimer(c)
    c.showPage()
    c.setFont(FONT, FONT_SIZE)
    watermark(c)

def draw_text(string, text, font, size, width, leading=None):
    if leading:
        text.setFont(font, size, leading=leading)
    else:
        text.setFont(font, size)
    font = pdfmetrics.getFont(font)
    if font.stringWidth(string, size) > width:
        bits = string.split(' ')
        while bits:
            did_something = False

            for i in range(1, len(bits) + 1):
                if font.stringWidth(' '.join(bits[:i]), size) > width:
                    if i == 1:
                        i = 2
                    text.textLine(' '.join(bits[:i - 1]))
                    bits = bits[i - 1:]
                    did_something = True
                    break

            if not did_something:
                text.textLine(' '.join(bits))
                break
    else:
        text.textLine(string)

def draw_candidate(c, number, family, given, party, i, tl, br, box_gap):
    number = str(number)
    font = pdfmetrics.getFont(FONT)

    c.rect(tl[0] + 1 * mm,
           tl[1] - 3 * mm - i * box_gap - (i + 1) * BOX_SIZE,
           BOX_SIZE, BOX_SIZE)
    width = font.stringWidth(number, FONT_SIZE + 1.0)
    c.setFont(FONT, FONT_SIZE + 1.0)
    c.drawCentredString(tl[0] + 1.1 * mm + BOX_SIZE / 2.0,
                        tl[1] - 2.3 * mm - i * box_gap - (i + 1) * BOX_SIZE + 1.5 * mm,
                        number)
    text = c.beginText(tl[0] + 2 * mm + BOX_SIZE,
                       tl[1] - 3 * mm - i * box_gap - i * BOX_SIZE - 4.5)
    text.setFont(FONT + '-Bold', CANDIDATE_FONT_SIZE,
                 leading=1.1 * CANDIDATE_FONT_SIZE)
    text.textLine(family)
    draw_text(given, text, FONT, CANDIDATE_FONT_SIZE, LABEL_WIDTH,
                leading=CANDIDATE_FONT_SIZE)
    if party:
        draw_text(party.upper(), text, FONT, PARTY_FONT_SIZE, LABEL_WIDTH)
    c.drawText(text)

    c.setFont(FONT, FONT_SIZE)

def generate(state_only, division, div_ticket, state, sen_ticket):
    container = cStringIO.StringIO()
    c = canvas.Canvas(container, A4R)

    watermark(c)

    c.setLineWidth(0.1)
    c.setStrokeColor(black)
    c.setFont(FONT, FONT_SIZE)

    font = pdfmetrics.getFont(FONT)

    groups = ballots[state]
    if not state_only:
        division_name, candidates = ballots[division]
    row = 0
    col = 0

    if not state_only:
        if len(candidates) > 13:
            box_gap = DIVISION_BOX_GAP
        else:
            box_gap = BOX_GAP
        division_height = len(candidates) * (BOX_SIZE + box_gap) + box_gap
        tl = (LEFT_MARGIN + col * GROUP_WIDTH, PAGE_HEIGHT - TOP_MARGIN)
        br = (tl[0] + GROUP_WIDTH, tl[1] - division_height)

        width = font.stringWidth(division_name, FONT_SIZE)
        offset = (GROUP_WIDTH - width) / 2

        c.setFillColorRGB(0.8745, 0.94117, 0.84705)
        c.rect(tl[0], br[1], GROUP_WIDTH, division_height, fill=1)
        c.setFillColor(black)

        for i in range(0, len(candidates)):
            family, given, party = candidates[i]
            number = div_ticket.pop(0)
            draw_candidate(c, number, family, given, party, i, tl, br, box_gap)

        tl = (LEFT_MARGIN + GROUP_WIDTH, PAGE_HEIGHT - TOP_MARGIN)
        br = (tl[0] + GROUP_WIDTH, tl[1] - division_height)

        text = c.beginText(tl[0] + 2 * mm, tl[1] - 5 * mm)
        draw_text(DIVISION_TEXT.format(division_name.upper()), text, FONT + '-Bold',
                  FONT_SIZE, GROUP_WIDTH - 4 * mm)
        text.textLine('')
        text.textLine('')
        draw_text(STATE_TEXT.format(STATES[state].upper()), text, FONT + '-Bold',
                  FONT_SIZE, GROUP_WIDTH - 4 * mm)
        c.drawText(text)

    row_height = PAGE_HEIGHT - TOP_MARGIN
    first_page = True

    def group_block_iterator(groups):
        index = 0
        while index < len(groups):
            page_end = yield 2, groups[index:index + GROUPS_PER_ROW - 2]
            if page_end:
                break
            index += GROUPS_PER_ROW - 2
        for block in range(index, len(groups), GROUPS_PER_ROW):
            yield 0, groups[block:block + GROUPS_PER_ROW]

    group_blocks = group_block_iterator(groups)
    for col_offset, block in group_blocks:
        max_candidates = max([len(g['candidates']) for g in block])
        group_height = max_candidates * (BOX_SIZE + BOX_GAP) + 2 * mm
        tl = None
        br = None

        if row_height <= group_height + GROUP_ROW_GAP:
            end_page(c)
            row_height = PAGE_HEIGHT - TOP_MARGIN
            if first_page:
                first_page = False
                col_offset, block = group_blocks.send(True)
                max_candidates = max([len(g['candidates']) for g in block])
                group_height = max_candidates * (BOX_SIZE + BOX_GAP) + 2 * mm

        for col, group in enumerate(block):
            col += col_offset

            if not group['label'].startswith('UG'):
                group_label = "Group " + group['label']
            else:
                group_label = 'Ungrouped'

            width = font.stringWidth(group_label, FONT_SIZE)
            offset = (GROUP_WIDTH - width) / 2

            tl = (LEFT_MARGIN + col * GROUP_WIDTH, row_height)
            br = (tl[0] + GROUP_WIDTH, tl[1] - group_height)

            c.drawString(tl[0] + offset, tl[1] - mm, group_label)
            c.line(tl[0] + offset - 0.5 * mm, tl[1], tl[0], tl[1])
            c.line(tl[0], tl[1], tl[0], br[1])
            c.line(tl[0], br[1], br[0], br[1])
            c.line(br[0], tl[1], tl[0] + offset + width + 0.5 * mm, tl[1])

            col += 1

            for i in range(0, len(group['candidates'])):
                family, given, party = group['candidates'][i]
                number = sen_ticket.pop(0)
                draw_candidate(c, number, family, given, party, i, tl, br, BOX_GAP)

        c.line(br[0], br[1], br[0], tl[1])
        row_height -= group_height + GROUP_ROW_GAP

    disclaimer(c)
    c.save()

    return container.getvalue()

def setup_rollbar(environment):
    if 'ROLLBAR_TOKEN' not in os.environ:
        return
    rollbar.init(os.environ['ROLLBAR_TOKEN'], environment,
                 allow_logging_basic_config=False)

@app.route('/pdf', methods=['POST'])
def pdf():
    try:
        state_only = bool(int(request.form['state_only']))
        senate_ticket = request.form['senate_ticket'].split(',')

        if not state_only:
            division = request.form['division']
            division_ticket = request.form['division_ticket'].split(',')
        else:
            division = None
            division_ticket = None

        pdf = generate(state_only, division, division_ticket,
                       request.form['state'], senate_ticket)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
	    'attachment; filename=ballot.pdf'
        return response
    except:
        rollbar.report_exc_info()
        raise

if __name__ == '__main__':
    setup_rollbar('debug')
    app.run(debug=True, port=5002)
else:
    setup_rollbar('production')
