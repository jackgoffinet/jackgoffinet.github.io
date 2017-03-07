---
layout: post
title: "Listening to the Mandelbrot Set"
description: "How to simulate the Mandelbrot set on a record player"
date: 2017-03-07
tags: [mandelbrot, math, music, audio]
comments: false
share: true
use_math: true
---

The Mandelbrot set is a subset of the complex numbers defined by

$$M = \{c \in \mathbb{C} \vert \exists r \in \mathbb{R}^+ {}_{\ni} \forall n \in \mathbb{Z}^+, \vert f_n(c)\vert \leq r\}$$

where $$f_1(z) \equiv z$$ and $$f_n(z) \equiv [f_{n-1}(z)]^2 + z$$ for all $$n>1$$.
In other words, $$M$$ is the set of complex numbers $$c$$ such that the repeated compositions of the
mapping $$z \mapsto z^2 + c$$ remain bounded.

It looks something like this:

<img src="{{ site.url }}/images/mandelbrot.png" width="600" align="middle" alt="mandelbrot plot">

It's a [fractal](http://mathworld.wolfram.com/Fractal.html),
so it displays self-similarity on all scales and is endlessly detailed.
Now imagine a record player's needle tracing along the shape's perimeter, starting off
very fast, circling the shape many times a second, and then gradually slowing down,
approaching a standstill.
If the Mandelbrot set's grooves were like those of a normal record, you would hear the
music slowing down while its frequencies dropped to inaudible ranges. Eventually,
you would hear nothing at all, even if you amplified the sound to arbitrary volumes.
But the Mandelbrot set's grooves are not like a record's. They have
endless detail, so an imaginary needle tracing them would never "run
out" of frequencies to produce. We can hear frequencies between about 20 and 20,000
Hz, so as the needle slows down, lower frequencies slide off the bottom end,
just as with a normal record, but at the same time inaudibly high frequencies become audible,
and this process continues indefinitely.

### Approximating the Mandelbrot Set

It can be shown that $$M \subset \overline{B}(0,2)$$, so we can write:

$$ M = \{c \in \mathbb{C} \vert \forall n \in \mathbb{Z}^+, \vert f_n(c)\vert \leq 2\}$$

In practice, a maximum number of iterations $$k \in \mathbb{Z}^+$$ is set so that we
can define

$$M_k = \{c \in \mathbb{C} \vert \forall n \leq k, \vert f_n(c)\vert \leq 2\}$$

as an approximation of $$M$$. Note that $$M \subset M_k$$. The following Python
function, adapted from [this](https://www.ibm.com/developerworks/community/blogs/jfp/entry/my_christmas_gift?lang=en)
useful blog post, determines membership in $$M_k$$:

```python
def in_mandelbrot(c, k):
  z = c
  for i in range(1,k):
    if abs(z) > 2:
      return False
    z = z**2 + c
  return abs(z) <= 2
```
This algorithm is useful for creating binary color images of the
Mandelbrot set like the one above, but for our purposes it's useful to define a scalar
function $$\widetilde{M}_k: \mathbb{C} \times \mathbb{R} \rightarrow \mathbb{R}^+ \cup \{-1\}$$
that maps a complex number $$c$$ and a real $$h \gg 2$$, called the *horizon*,
to a measure of how "close" $$c$$ is to being in the Mandelbrot set. The details
aren't necessary, but can be found, again,  [here](https://www.ibm.com/developerworks/community/blogs/jfp/entry/my_christmas_gift?lang=en).
What's important to us is that $$c$$ with large $$\widetilde{M}_k(c,h)$$ are
"closer" to $$M$$ in some sense, but not in $$M$$, while $$c$$ such that
$$\widetilde{M}_k(c,h) = -1$$ are thought, but not gauranteed, to be in $$M$$.
The following Python function computes $$\widetilde{M}_k(c,h)$$:

```python
import numpy as np

def in_tilde_mandelbrot(c, h, k):
  c = z
  for i in range(1,k):
      if abs(z) > h:
          log_h = np.log(np.log(h))/np.log(2)
          return i - np.log(np.log(abs(z)))/np.log(2) + log_h
      z = z**2 + c
  return -1
```
### Charting the Needle's Trajectory

Now consider the contour lines of $$\widetilde{M}_k(c,h)$$, the sets of $$c$$ such
that $$\widetilde{M}_k(c,h)$$ is constant. As $$k$$, $$h$$, and
$$x \in \mathbb{R}$$ approach infinity,
$$\{c \vert \widetilde{M}_k(c,h) \geq x\}$$ approaches the perimeter of the Mandelbrot set.
So we will have the needle trace the contour lines of $$\widetilde{M}_k(c,h)$$, continuously
increasing the value being traced, hugging the Mandelbrot set's perimeter more and
more closely, all the while slowing down. The result is a sequence of points
$$z_1, z_2, \dots, z_j$$ that look like this when connected by line segments:

<img src="{{ site.url }}/images/mandelbrot_trace.png" width="400" align="middle" alt="mandelbrot trace">

Now all we need to do is to "unroll" the trajectory in a complex plane into a
single-valued function $$f$$ of one variable, time. First, apply a discrete gaussian blur
to the sequence to clean up some of the noise. Then look at each consecutive pair
of sequence elements, $$z_i$$ and $$z_{i+1}$$ for $$i<j$$. They will have roughly
the same value of $$\widetilde{M}_k$$, call it $$p$$. Fix some $$\delta \in \mathbb{R}^+$$
and search for the nearest complex number $$c$$ on the line equidistant from $$z_i$$ and
$$z_{i+1}$$ such that $$\widetilde{M}_k(c,h) = p + \delta$$. If such a point does
not exist, find $$\DeclareMathOperator*{\argmax}{argmax} \argmax_{c}\widetilde{M}_k(c,h)$$,
the point $$c$$ with $$\widetilde{M}_k(c,h)$$ closest to $$p + \delta$$. In other
words, $$c$$ is a point on a contour line that is a more precise approximation
of the perimeter of $$M$$. Compared to the contour line described by
$$\widetilde{M}_k(c,h) = p$$, it has more elaborate oscillations and therefore
higher frequencies, which is exactly what we want.

Finally, define $$f(i) = \vert \frac{z_i+z_{i+1}}{2} - c\vert$$. For each $$i$$ the function
$$f$$ describes the oscillations of the countour line $$\widetilde{M}_k(c,h) = p + \delta$$
relative to the oscillations of the contour line $$\widetilde{M}_k(c,h) = p$$.
Apply a discrete gaussian blur and a sliding window normalization to $$f$$ and,
voila, we have an audio file!

<iframe width="100%" height="166" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/311256385&amp;color=ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false"></iframe>
