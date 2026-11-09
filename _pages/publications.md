---
layout: archive
title: Publications
permalink: /publications/
section: research
intro: Research on microbial genomes, active learning and biological discovery.
excerpt: Publications by Ricardo Valencia Albornoz on active learning, metabolomics and microbial genomics.
---
<div class="archive-toolbar"><p>{{ site.publications.size }} publications</p><a href="{{ site.author.googlescholar }}">Google Scholar <span aria-hidden="true">↗</span></a></div>
<div class="publication-list">{% assign papers = site.publications | sort: 'date' | reverse %}{% for paper in papers %}{% include publication-row.html paper=paper %}{% endfor %}</div>
