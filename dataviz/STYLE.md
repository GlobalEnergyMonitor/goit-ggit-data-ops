# GEM figure style

This is a copy of GEM's data visualization rules, checked on 2026-11-19. The authority is the style guide page, not this file. If the two disagree, the page wins, and this file and `tokens.json` should be updated to match.

- Style guide: https://globalenergymonitor.org/data-visualization-style-guide
- GEM color notebook: https://observablehq.com/d/76aaf1373f5dfdab

The values below are also in [tokens.json](tokens.json), which is what the code reads. Change a value there, not in a figure.

## Text

- Title, subtitle, source and note use Plus Jakarta Sans.
- Legends, map labels, axes and annotations use Barlow Semi Condensed.
- All text is #3A4A50.
- Title: 28 px, bold, line height 1.2.
- Subtitle: 18 px, regular, line height 1.45.
- Legend, labels and annotations: 16 px, regular.
- Source and note: 14 px, regular, line height 1.2.
- Nothing is smaller than 14 px. Map labels count as body text, so they are 16 px.

## Colors

Brand colors:

| Name | Hex |
|------|-----|
| Midnight | #002430 |
| Navy | #004A63 |
| Teal | #016B83 |
| Orange | #FE4F2D |
| Mint | #A5E9E4 |
| Warm white | #F2F2EB |
| White | #FFFFFF |

Categories, in this order. The five are chosen to work for colorblind readers.

| Name | Hex |
|------|-----|
| Teal | #016B83 |
| Orange | #FE4F2D |
| Indigo | #4A57A8 |
| Deep red | #7F142A |
| Green | #65BD8B |

Four more for when five are not enough: blue #099ED8, clay red #CA4A50, midnight green #004F61, midnight purple #061F5F.

Background grey for anything that should sit behind the main subject: #BECCCF.

Single-color scales, darkest first. Use at most four shades. Darker means operating or further along. Lighter means earlier stage.

- Fossil: #5D0E1E, #A93841, #DF8182, #F6C9C6
- Renewables: #015F74, #058BB8, #1EAEE6, #8CD3EF
- Grey: #4C6267, #6E8C91, #BECCCF, #DCE3E5. Grey is for retired and canceled projects, or for background.

## Layout

- A figure is at most 800 px wide, including its header and footer. The kit fixes the width at 800, so a PNG exported at 2x is 1600 px wide.
- Header and footer are left-aligned.
- The subtitle sits 8 px below the title.
- There are 32 px between the header and the body, and between the body and the footer.
- In the footer, the source line comes first and the note comes below it.
- The GEM logo sits at the bottom right, 40 px high, with a 28 px margin, in teal #016B83.
- Legend samples are square, 16 px apart, with 4 px between a sample and its label.
- Annotation lines are 2 px in #3A4A50, and annotation text has a white outline.
- Gridlines on charts are #CBCBCB, 0.5 px, solid, at reduced opacity.

## Maps

- Water is #C8D5D9.
- Land is #F2F2EB.
- A country the map is about can be filled #C2C2C2 at 20 to 30 percent opacity.
- Borders are #555555, 1 px. Country borders are at 40 percent opacity. State and province borders are at 18 percent.
- The usual pipeline map uses orange for the lines the map is about, solid for in construction and dashed for proposed, with the operating network in background grey and terminals in teal.

## Where the kit departs from the guide

- The gap between a legend sample and its label is 10 px, not 4 px. The guide's 4 px is written for small square swatches. The kit's legends show a line sample, which reads badly that close to its label.

## Check before publishing

1. The title states the main point in one short sentence. The subtitle says what is plotted.
2. No label overlaps a line, a point or another label. Labels are placed by hand in pixels, so check every one after changing the map height or the map window.
3. Every category in the legend is on the map, and nothing on the map is missing from the legend.
4. The source line names the tracker and the month of the data. The note says anything a reader needs to read the map correctly, including what was left off.
5. The PNG is 1600 px wide and the text is sharp.
6. No hex code is typed into the figure's `map.js`.
