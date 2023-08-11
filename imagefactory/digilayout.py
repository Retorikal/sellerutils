#!/usr/bin/python3
from urllib.error import HTTPError
from os.path import exists
from xml.etree import ElementTree
from datetime import datetime
import argparse
import requests
import cairosvg
import copy
import math
import wget
import cairosvg
import xml
import sys
import re
import os
import bs4

now = datetime.now
default_template = "template/template_a3_port.svg"
default_outdir = "imagcache/"
global_images_cache = "imagcache/cardimg/"
jp_url = "https://en.digimoncard.com/images/cardlist/card/{}.png"


def craft_dictionary():
  regexes = {
    "card_name": r'card_name">(.*)<',
    "card_id": r'<div class="card_img">.*\n.*images/cardlist/card/(.*)(_P.)?.png',
  }
  # name to get name, id to get card id and para id


def get_card_images(cardlist):
  decklist = open(cardlist)
  cardlist = []

  print("Parsing cardlist and downloading images..")
  for entry in decklist.readlines():
    result = re.search(r"(/*)([0-9]) (.*?)\s*(\w+-[0-9]+)", entry)
    if result == None or result.group(1) != "":
      continue

    count = int(result.group(2))
    name = result.group(3)
    code = result.group(4)
    cardlist.extend([code for _ in range(count)])

    print("Downloading {}'s ({}) image".format(name, code))
    if not exists(global_images_cache + imgpath(code)):
      try:
        wget.download(jp_url.format(code), "./" +
                      global_images_cache + imgpath(code))
      except HTTPError as e:
        wget.download(jp_url.format(code), "./" +
                      global_images_cache + imgpath(code))
      print("")
  print("\nImage download done.")

  return cardlist


def craft_thumbnails(svg_string, cardlist, outname):

  tree = ElementTree.parse(svg_string)
  trbk = copy.deepcopy(tree)

  cardslots = tree.getroot().findall(
      "./{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}g[@id='imagesgroup']/")
  backslots = trbk.getroot().findall(
      "./{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}g[@id='imagesgroup']/")
  slotcount = len(cardslots)
  cardcount = len(cardlist)
  printcount = math.ceil(cardcount / slotcount)

  print("You will need to print {} times ({} cards each).".format(
      printcount, slotcount))

  last_slot_id = cardslots[-1].attrib["id"]
  dimensions = (int(last_slot_id[-2]), int(last_slot_id[-1]))

  print("Template dimensions: {} (height, width) in cards".format(dimensions))

  printed_count = 0
  # Iterate for all print slots available
  for i in range(slotcount * math.ceil(cardcount / slotcount)):
    cardslot = cardslots[i % slotcount]
    cardcode = cardlist[i] if i < len(cardlist) else ""

    # assign face card image
    cardslot.attrib[img_attrib] = imgpath(
        cardcode) if cardcode != "" else tama_url

    # assign backing card image
    index = i % slotcount
    row = index // dimensions[1]
    col = index % dimensions[1]
    position = row * dimensions[1] + (dimensions[1] - col) - 1
    backslot = backslots[position]
    backslot.attrib[img_attrib] = tama_url if cardcode in digitama_list else back_url

    if i % slotcount == slotcount - 1:
      printed_count += 1
      facename = "{}{}-{}-face.svg".format(
          output_location, outname, printed_count)
      backname = "{}{}-{}-back.svg".format(
          output_location, outname, printed_count)
      facepdfname = "{}{}-{}-face.pdf".format(
          output_location, "pdf" + outname, printed_count)
      backpdfname = "{}{}-{}-back.pdf".format(
          output_location, "pdf" + outname, printed_count)
      tree.write(facename)
      trbk.write(backname)
      cairosvg.svg2pdf(url=facename, write_to=facepdfname)
      cairosvg.svg2pdf(url=backname, write_to=backpdfname)

      print(
          "Finished crafting svg for print [{}/{}] \r".format(printed_count, printcount))


def get_identifier(template_name):
  identifier_regex = re.search(r"([A-Z]\S+)\..*$", template_name)
  if identifier_regex == None or identifier_regex.group(1) == "":
    print("Template file does not contain correct identifier string")
    return None

  return identifier_regex.group(1).upper()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Tokopedia Shop Thumbnail Generator")
  parser.add_argument('template', metavar='template',
                                          type=str, help='svg template file')
  parser.add_argument('-t', metavar='translate', type=str,
                      help="json file to translate card number to label string", default=default_template)
  args = parser.parse_args()

  template = args.template
  translate = args.t

  identifier = get_identifier(template)
  print("Identifier:", identifier)

  get_card_images(["P-075_P2"])

  svg_str = open(template).read()
  dictionary = {"P-075_P2": ["Okuwamon", "Tamer Battle Pack"]}
  craft_thumbnails(svg_str, )

  images_cache = os.path.join(global_images_cache, identifier)
  if not os.path.exists(images_cache):
    os.makedirs(images_cache)

  # template = args.t
  # outname = args.o

  # cardlist= parse_cards(args.filename)
  # modify_svg(template, cardlist, outname)

  # print("Finished. Enjoy your proxies!")


bs4.BeautifulSoup("<br/>", 'html.parser')
