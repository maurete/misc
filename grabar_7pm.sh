#!/usr/bin/env bash
NOW=$(date +%F)
cvlc --run-time=5000 http://streaming.urbana.com.uy/urbana --sout "#duplicate{dst=std{access=file,mux=raw,dst=/home/mauro/7pm-$NOW.mp3}" vlc://quit ;