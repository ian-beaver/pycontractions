PyContractions
==============

A Python library for expanding and creating common English `contractions <https://en.wikipedia.org/wiki/Contraction_(grammar)>`_ in text.  This is very useful for dimensionality reduction by normalizing the text before generating word or character vectors.  It performs contraction by simple replacement rules of the commonly used English contractions.

Expansion, on the other hand, is not as simple as it requires contextual knowledge in order to choose the correct replacement words.  Consider the following rules::

    I'd -> I would
    I'd -> I had


How to automatically decide which rule to use for each match in the following text?

    *I'd like to know how I'd done that!*

This library takes a three-pass approach.  First, the simple contractions with only a single rule are replaced.  On the second pass if any contractions are present with multiple rules we proceed to replace all combinations of rules to produce all possible texts.  Each text is then passed through a grammar checker and the `Word Mover's Distance <http://proceedings.mlr.press/v37/kusnerb15.pdf>`_ (WMD) is calculated between it and the original text.  The hypotheses are then sorted by least number of grammatical errors and shortest distance from the original text and the top hypothesis is returned as the expanded form.

The grammatical error count eliminates the worst choices, but there are many cases that contain no or the same number of grammatical errors.  In these cases the WMD works as the tie-breaker.  WMD is the minimum weighted cumulative cost required to move all words from the original text to each hypothesis.  This leverages the underlying `Word2Vec <https://arxiv.org/pdf/1301.3781.pdf>`_, `GloVe <http://www.aclweb.org/anthology/D14-1162>`_, or `FastText <https://research.fb.com/wp-content/uploads/2017/06/tacl.pdf>`_, or any semantic vector model chosen.  As the difference between each hypothesis is only the replacement of a contraction with it's expansion, the "closest" hypothesis to the original text will be that with the minimum Euclidean distance between the contraction and expansion word pair in the embedding space.

Using the `Google News pre-trained model <https://code.google.com/archive/p/word2vec/>`_ yields good results but there are still some cases that can cause problems.  Consider the following rules::

    ain't -> am not
    ain't -> are not
    ain't -> is not
    ain't -> has not
    ain't -> have not

And the following sentence:

    *We ain't all the same*

The output hypotheses using the Google model will look like this (Hypothesis, WMD, # Grammar Errors)::

    [('We have not all the same', 0.6680542214210519, 0),
     ('We are not all the same', 0.7372250927409768, 0),
     ('We has not all the same', 0.7223834627019157, 1),
     ('We am not all the same', 0.8113022453418426, 1),
     ('We is not all the same', 0.6954222661000212, 2)]

Notice that the grammar checker eliminates the worst offenders, but two remain with no grammar errors.  Among other reasons, the past-tense *have* is more commonly embedded between "we" and "not" than the present-tense *are* in the Google News dataset, therefore it yields a lower travel cost to hypothesis 1 than hypothesis 2.  Trying the FastText 1 million word vector 300 dimensional model we see::

    [('We have not all the same', 0.45723494251012825, 0),
     ('We are not all the same', 0.46916066501924986, 0),
     ('We has not all the same', 0.49631577238129004, 1),
     ('We am not all the same', 0.5491228638094231, 1),
     ('We is not all the same', 0.4898885599267869, 2)]

While the first result is still incorrect, the second and third have swapped position by distance.  This model is much closer to providing the correct expansion.  Like anything using models, your mileage will vary based on the embedding model you use and how well it matches your data.  In general, however, the approach works well enough for many pre-processing tasks.

For performance, an optimized version works under the assumption that every instance of a particular contraction should be expanded the same.  This is generally the case in short texts like Tweets or IRC chats.  For longer texts such as comments or webpages the slower but more accurate approach will yield better results.



Example usage
-------------

.. code:: python

    >>> from pycontractions import Contractions
    
    # Load your favorite semantic vector model in gensim keyedvectors format from disk
    >>> cont = Contractions('GoogleNews-vectors-negative300.bin')
    
    # or specify any model from the gensim.downloader api
    >>> cont = Contractions(api_key="glove-twitter-100")
    
    # or train or load your own keyedvectors model and pass it in
    >>> cont = Contractions(kv_model=mykvmodel)
    
    # optional, prevents loading on first expand_texts call
    >>> cont.load_models() 

The faster less precise version is the default:

.. code:: python

    >>> list(cont.expand_texts(["I'd like to know how I'd done that!",
                                "We're going to the zoo and I don't think I'll be home for dinner.",
                                "Theyre going to the zoo and she'll be home for dinner."]))
     [u'I had like to know how I had done that!',
      u'we are going to the zoo and I do not think I will be home for dinner.',
      u'they are going to the zoo and she will be home for dinner.']    

Notice the error in the first text is correct below when using ``precise=True``:

.. code:: python

    >>> list(cont.expand_texts(["I'd like to know how I'd done that!",
                                "We're going to the zoo and I don't think I'll be home for dinner.",
                                "Theyre going to the zoo and she'll be home for dinner."], precise=True))
     [u'I would like to know how I had done that!',
      u'we are going to the zoo and I do not think I will be home for dinner.',
      u'they are going to the zoo and she will be home for dinner.']



To insert contractions use the ``contract_texts`` method:

.. code:: python

    >>> list(cont.contract_texts(["I would like to know how I had done that!",
                                  "We are not driving to the zoo, it will take too long.",
                                  "I have already tried that and i could not figure it out"]))
     [u"I'd like to know how I'd done that!",
      u"We aren't driving to the zoo, it'll take too long.",
      u"I've already tried that and i couldn't figure it out"]



Performance differences using the ``precise`` version on an Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz:

.. code:: python

    >>> cont = Contractions(api_key="glove-twitter-25")
    >>> cont.load_models()
    
    >>> text = "Theyre going to the zoo and she'll be home for dinner."
    >>> %timeit list(cont.expand_texts([text]))
    10 loops, best of 3: 21.4 ms per loop
    >>> %timeit list(cont.expand_texts([text], precise=True))
    10 loops, best of 3: 25.1 ms per loop
    
    # A 349 word movie review    
    >>> len(text.split())
    349
    >>> %timeit list(cont.expand_texts([text]))
    1 loop, best of 3: 1.17 s per loop
    >>> %timeit list(cont.expand_texts([text], precise=True))
    1 loop, best of 3: 2.88 s per loop
    
    # Contraction is fast, same 349 word movie review
    >>> %timeit list(cont.contract_texts([text]))
    100 loops, best of 3: 4.77 ms per loop



Installation
------------

To install via pip::

    $ pip install pycontractions


Prerequisites
-------------

- `language-check <https://github.com/myint/language-check>`_
- `gensim <http://radimrehurek.com/gensim/>`_

language-check depends on the Java `LanguageTool <https://www.languagetool.org>`_ package, 
therefore this package depends on it (and Java 6.0+).  The language-check installer *should* take care of 
downloading it for you, but it may take several minutes depending on internet connection.
