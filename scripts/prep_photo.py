#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import cv2, numpy as np
from PIL import Image
from rembg import remove
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(); p.add_argument('input',type=Path); p.add_argument('output',type=Path,nargs='?',default=ROOT/'source-prepped.png'); a=p.parse_args()
    source=Image.open(a.input).convert('RGBA'); cutout=remove(source); rgb=np.array(cutout.convert('RGB')); alpha=np.array(cutout.getchannel('A'),dtype=np.float32)/255.0
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY); gray=cv2.createCLAHE(clipLimit=2.5,tileGridSize=(8,8)).apply(gray); gray=cv2.convertScaleAbs(gray,alpha=1.04,beta=15); alpha=cv2.GaussianBlur(alpha,(0,0),0.9)
    result=np.clip(gray.astype(np.float32)*alpha+255.0*(1.0-alpha),0,255).astype(np.uint8); Image.fromarray(result,mode='L').save(a.output); print(f'Wrote {a.output}')
if __name__=='__main__': main()
