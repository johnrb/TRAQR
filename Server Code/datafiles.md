---
layout: page
title: Datafiles
permalink: "/datafiles/"
---

Raw (JSON) data files are stored on this page.

For example, `fake_data.json` contains randomly generated data points scattered across the county (just for testing).
`combined_data.json` is what's currently displayed on the [map](../map).

### Files:
{% directory path: datafiles %}
  <a href="..{{ file.url }}" >{{ file.name }}</a>
{% enddirectory %}
