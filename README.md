# World News — 18 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![make.fun rank](https://make.fun/badge/news-image-20261118/Sandi207/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![make.fun reward](https://make.fun/badge/news-image-20261118/Sandi207/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

An editorial front page summarising the verified world news for Wednesday 18 November 2026 in one 1024×1024 image. Original inline SVG illustrations, clear headlines, and a prominent date make each story understandable from the image alone. The finished `entry.png` is stored in the repository, and `main.ts` copies it unchanged using only the Node standard library, with no network or rendering required in the grader.

The six main stories:

- **NVIDIA:** Record quarterly revenue of $115.8 billion, up 103% year on year, in its first earnings since founder Jensen Huang resigned as CEO. The board does not intend to reinstate him; Colette Kress is interim CEO, and the next-quarter forecast is $130 billion.
- **Trump in Manila:** US President Donald Trump arrives in Manila, Philippines, for Quad talks with India, Japan and Australia, ahead of a China visit and the APEC summit.
- **Ukraine:** Flamingo cruise missiles destroy a road span of the Kerch Bridge linking Russia to occupied Crimea; Russia pounds bridges in Kyiv in return.
- **Iran–US Gulf standoff:** The IRGC claims its drones hit a US radar at Sheikh Isa Air Base in Bahrain. US Central Command says they were intercepted with no damage or injuries; US jets strike an IRGC missile site on Qeshm Island in response.
- **UK sanctions:** Britain sanctions eight firms over illegal West Bank settlements, in a push to protect the two-state solution.
- **Cyclone Akvan:** The cyclone intensifies over the Bay of Bengal; Andhra Pradesh and Odisha are on high alert.

The footer includes India's record 10th SAFF Championship football title after beating Pakistan 2-1, MS Dhoni's IPL retirement and new role as Chennai Super Kings mentor, and the announcement of Grammy 2027 nominations.

Run with Node 22 or later; `main.ts` contains only JavaScript-compatible syntax:

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

The default output is `/output/entry.png`. Rebuild locally with `python3 render.py`, which uses only Pillow and the system DejaVu and Liberation fonts to draw the design specified in `entry.html`. No browser is required. Neither building nor running downloads assets or fetches news.
