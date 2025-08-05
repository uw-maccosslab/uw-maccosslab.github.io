---
layout: default
title: News
permalink: /news/
---
*News is updated regularly. For real-time updates follow us on social media.*

### Social Media & Online Presence
- **BlueSky:** [@maccoss.bsky.social](https://bsky.app/profile/maccoss.bsky.social)
- **LinkedIn:** [MacCoss LinkedIn](https://www.linkedin.com/in/maccoss/)

---

# Lab News & Updates

Subscribe to our RSS feed for automatic updates: [RSS Feed](/feed.xml)

## Recent News

{% for post in site.posts limit:10 %}
<div class="news-item">
  <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
  <div class="post-excerpt">
    {{ post.content }}
  </div>
  {% if post.categories.size > 0 %}
    <p class="post-categories">
      {% for category in post.categories %}
        <span class="category-tag">{{ category }}</span>
      {% endfor %}
    </p>
  {% endif %}
</div>
<hr>
{% endfor %}

