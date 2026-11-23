# The World in One Image — Monday 23 November 2026

A program whose output is one image summing up the world's news of
**Monday 23 November 2026**: a one-page newspaper with 59 stories, all
happening or first reported that day.

## What the image holds

- Masthead naming the day in full: **MONDAY 23 NOVEMBER 2026**
- A UTC timeline strip of the day (01:15–07:32 UTC)
- Three illustrated leads: COP31 ends with no climate deal · Democrats
  clinch 258 US House seats · Russian strikes kill 11 near Kyiv
- 14 numbered story tiles, each with a verification badge
  (CONFIRMED / REPORTED / CLAIM) and a named source
- A world map, "WHERE IT HAPPENED", with numbered pins matching the tiles
- A DATE CHECK box listing famous older stories deliberately left out
  (Shenzhen summit 19 Nov, missiles in Poland 20 Nov, GPT-6.2 launch
  17 Nov, Nvidia CEO exit 12 Nov, US measles status 17 Nov)
- A 42-line index of the rest of the day, every line badged

## Run it

```
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3, standard library only) copies the shipped
`entry.png` to the output directory. It runs offline and writes the same
bytes every run. `entry.png` is 1024×1024, PNG, under 1 MiB.

## Rebuild the image

`build_front_page.py` renders `entry.png` deterministically from
`news.json` (the story corpus: headline, summary, source and status for
all 59 stories) with Pillow and fixed system fonts.

## License

MIT — see `LICENSE`.
