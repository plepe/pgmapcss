Example 1: Major roads and parks
================================
For starters a simple example will be shown: Major roads and parks.

![example1](example1.png)
```css
/* draw a green polygon for all parks */
area[leisure=park] {
  fill-color: #00af00;
}
/* print a label on all parks */
area[leisure=park]::label {
  text: eval(tag(name));
  font-family: "DejaVu Sans Oblique";
  font-size: 9;
  text-color: #005f00;
  z-index: 3;
}

/* all major roads will be rendered with a 2px black line */
line|z12-[highway=primary],
line|z12-[highway=secondary],
line|z12-[highway=tertiary] {
  color: #000000;
  width: 2;
  z-index: 1;
}
/* and a black label next to the line
   with a 50% transparent white halo */
line|z12-[highway=primary]::label,
line|z12-[highway=secondary]::label,
line|z12-[highway=tertiary]::label {
  text: eval(tag(name));
  text-offset: 9;
  text-color: #000000;
  text-halo-color: #ffffff7f;
  text-halo-radius: 1;
  z-index: 2;
}
```

