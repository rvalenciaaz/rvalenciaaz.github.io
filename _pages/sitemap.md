---
layout: archive
title: Sitemap
permalink: /sitemap/
excerpt: Find research, projects, talks and notes on Ricardo Valencia Albornoz’s website.
---
<div class="sitemap-grid"><section><h2>The essentials</h2><ul><li><a href="{{ '/' | relative_url }}">Home</a></li><li><a href="{{ '/publications/' | relative_url }}">Publications</a></li><li><a href="{{ '/talks/' | relative_url }}">Talks & presentations</a></li><li><a href="{{ '/portfolio/' | relative_url }}">Projects</a></li><li><a href="{{ '/year-archive/' | relative_url }}">Blog</a></li></ul></section><section><h2>Projects</h2><ul>{% for project in site.portfolio %}<li><a href="{{ project.url | relative_url }}">{{ project.title }}</a></li>{% endfor %}</ul><h2>Blog posts</h2><ul>{% for post in site.posts %}<li><a href="{{ post.url | relative_url }}">{{ post.title }}</a></li>{% endfor %}</ul></section></div>
