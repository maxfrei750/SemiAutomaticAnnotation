#!/usr/bin/env bash
convert -resize 600x600 image_D2_crack_Pos12_016.png image_D2_crack_Pos12_016.png visualization_D2_crack_Pos12_016.png \
  visualization_D2_crack_Pos12_016.png -delay 20 -morph 10 -layers 'optimize' demo.gif
