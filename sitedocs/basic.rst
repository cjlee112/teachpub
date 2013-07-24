#####################
Simple Remix Examples
#####################

Reusing content for many purposes
---------------------------------

A basic principle of teachpub.org is that anything you write
should be reusable to produce many different kinds of materials.
For example, from one piece of text you can produce

* slides (a la Powerpoint)
* document (a la Word)
* web page (to display your content online)

Try this out on the following simple example.
You may edit the example text (if you like), then select
the output you want and click "Go!".  After viewing the
output, click your browser's Back button to return to this page.
Note, if you change the text but your changes do not appear
in the formatted output, try clicking your browser's Refresh
button to force it to show the updated output.

.. raw:: html

   <form id="build1" method="GET" action="/build_html">
   <input type="hidden" name="fname" value="basic1"/>
   <input type="hidden" name="publicOnly" value="1"/>
   <textarea cols=80 rows=20 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: CS 121: Introduction to Bioinformatics

   Welcome to Bioinformatics!
   --------------------------

   *Bioinformatics is the study of the inherent structure of biological
   information.*

   * There is inherent structure: many kinds of patterns.
   * An ascending scale of problems from here to eternity...
   * Algorithms that solve the *pattern finding* problem.
   * Statistical metrics that distinguish *information* from 
     random *noise*.

   Forensic Test Factoring
   -----------------------

   Based on the information graphs for a. the *match* model;
   b. the *mismatch* model, indicate how you could
   factor the joint probability :math:`p(X,S|\theta)`, by writing
   the equation for this with appropriate parentheses to indicate which terms
   if any can be factored.  

   Forensic Test Factoring
   -----------------------

   For the *match* model

   .. math:: p(X,S|\theta) = 
      \sum_{\kappa}p(\kappa|\theta)p(X|\kappa)p(S|\kappa)

   For the *mismatch* model

   .. math:: p(X,S|\theta) =
      \left(\sum_{\kappa}p(\kappa|\theta)p(X|\kappa)\right)
      \left(\sum_{\lambda}p(\lambda|\theta)p(S|\lambda)\right)


   Half Your DNAs Is Belong to Us!
   -------------------------------

   .. image:: MAURY_POVICH_Mixtape_front.jpg

   Paternity Test Info Graph
   -------------------------

   After watching Maury Povitch you decide paternity testing would
   be more profitable.  You decide to use the exact same microarray
   measurements of SNP markers, from three samples: measurement X
   from the candidate dad; measurement C from the child;
   measurement M from the mother.  


   </textarea>
   <BR>Make:
   <select name="outputFormat">
   <option SELECTED value="html">web page</option>
   <option value="beamer">Slides</option>
   <option value="latex">Document</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

A few notes:

* this simple text format is called
  `reStructuredText <http://sphinx-doc.org/rest.html>`_.
  Anyone can learn it in 5 minutes.
* it supports many extensions like
  `LaTeX equations <http://www.latex-project.org/>`_
  (e.g. see the ``math`` tags above).



Remixing OpenCourseWare slides
------------------------------

teachpub.org uses a simple extension of this called
`ReUsableText <http://people.mbi.ucla.edu/leec/docs/reusabletext/>`_.
This lets you use ``select`` directives to remix
different materials.  In fact, you can remix anything on the
Internet.  Here for example we mix some of our own
content with slides from 
`OpenCourseWare <http://www.ocwconsortium.org/>`_
(whose license explicitly
permits such re-use with attribution):

.. raw:: html

   <form id="build2" method="GET" action="/build_html">
   <input type="hidden" name="fname" value="myfile"/>
   <input type="hidden" name="publicOnly" value="1"/>
   <input type="hidden" name="beamerTheme" value="default"/>
   <textarea cols=80 rows=20 name="selectText">
   :Author: (your name)
   :Organization: (your university)

   .. title:: Confounding Variables

   Overview
   --------

   * today we'll review some basic statistical issues in 
     analyzing association studies:

     * Confounding Variables
     * Solutions
   * slides from John McGready, Johns Hopkins Univ., via OpenCourseWare

   .. select:: http://ocw.jhsph.edu/courses/StatisticalReasoning2/PDFs/2009/SR2_lec2a_McGready.pdf
      * pages=5-9
      * pages=16-19

   </textarea>
   <BR>Make:
   <select name="outputFormat">
   <option value="beamer">Slides</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

Try it out!

Notes:

* this form of ``select`` will work with any URL on the Internet.
* on teachpub.org we restrict this to PDF files, for
  security reasons.
* you can mix materials from as many different source URLs as
  you want.

Remixing TeachPub.org content
-----------------------------

Remixing obviously becomes a lot more powerful with material that
is **open-source** (editable) rather than **closed-source**
(unmodifiable, e.g. PDF format).  For this reason, the primary mission
of teachpub.org is to provide a platform for sharing of open-source
teaching materials.  Currently, it contains approximately 1000
"units" of material drawn from bioinformatics and genomics
coursework.

We can use this material very flexibly, by mixing selected elements
with whatever additional things we want to say, e.g.:

.. raw:: html

   <form id="build3" method="POST" action="/build_html">
   <input type="hidden" name="fname" value="basic3"/>
   <textarea cols=80 rows=20 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: CS 121: Basic Hypothesis Testing

   Announcements
   -------------

   * Project 1 due today (email your code to the TA).
   * HW4 will be up on CourseWeb tonight.
   * Midterm is two weeks from today (Nov. 7).  We will give
     you practice exams and review sessions.
   * Today we have a few last notes about model building,
     and then proceed to hypothesis testing (our last
     "fundamentals" topic).

   .. select:: mongodb:
      * infograph_draw format=slide
      * var_vs_const format=slide
      * infograph_why format=slide

   Hypothesis Testing Definitions
   ------------------------------

   * We have some *hypothesis* *h* that we wish to test, i.e. a model.
   * Often this is just "the observations occurred by random
     chance", aka the "null hypothesis" :math:`h_0`.
   * We use some *observable* variable(s) *obs* to assess whether
     we should believe the hypothesis.
   * As usual, the connection between *h* and *obs* is the likelihood
     :math:`p(obs|h)`.
   * Simplest case of "boolean" prediction: :math:`H=\{h^+,h^-\}`,
     and a "test" observable :math:`T=\{t^+,t^-\}`.

   .. select:: mongodb:
      * error_types_jargon format=slide
      * twohybrid_fp_fn format=ctslide
      * twohybrid_mismatch format=slide

   ROC Curve for Assessing a Scoring Function
   ------------------------------------------

   * Parametric curve: for some *scoring function* :math:`S=score(X)`
     we define :math:`t^+` iff :math:`S \ge \alpha` for some
     threshold :math:`\alpha`.
   * Over some dataset :math:`X_1,X_2,...X_N` with *known* values
     :math:`H_1,H_2,...H_N` we can directly
     measure :math:`p(t^+|h^+),p(t^+|h^-)` for each possible value
     of :math:`\alpha`, and plot that as the **ROC curve**
     :math:`X=p(t^+|h^-,\alpha),Y=p(t^+|h^+,\alpha)`.
   * For completely random predictions, :math:`p(t^+|h^+)=p(t^+|h^-)`
     which is simply the diagonal line *Y=X* on the ROC plot.
   * Perfect predictor would acheive 100% True Positive Rate
     with 0% False Positive Rate, i.e. straight to the upper-left 
     corner.
   * Area-Under-Curve = 1 for perfect predictor, 0.5 for random
     (zero information) predictor.

   ROC Curve
   ---------

   .. image:: Roccurves.png
      :width: 70%

   .. select:: mongodb:
      * roc_error_fraction format=ctslide
      * roc_bayes format=slide
      * epsilon_test format=ctslide
      * pval_intro format=slide
      * why_extreme_test format=slide
      * pval_test format=slide
      * basic_snp_p_val format=ctslide

   </textarea>
   <BR>
   <select name="publicOnly">
   <option SELECTED value="1">Exclude private</option>
   <option value="0">Allow private</option>
   </select>
   questions (if you include private questions, you will be asked for a password). 
   <BR>Make:
   <select name="outputFormat">
   <option SELECTED value="html">web page</option>
   <option value="beamer">Slides</option>
   <option value="latex">Document</option>
   <option value="socraticqs">Socraticqs</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

Notes:

* ``mongodb`` is the back-end database for the teachpub.org 
  teaching materials repository.
* In the teachpub.org prototype,
  materials are selected by their unique identifier values.  
  The production version will make it easy for users by
  inserting these ID values automatically for materials
  they've picked from their search results.
* The ``format`` argument re-formats each selected content
  element using the specified **template**.  By separating
  *content* and *styles* in this flexible way, ReUsableText
  makes it easy to reuse any piece of content in many 
  different ways.  ReUsableText uses standard
  `Jinja2 <http://jinja.pocoo.org/>`_ templates;
  you can write your own templates to add or modify
  styles.
* note that some formats perform sophisticated tasks
  for you.  For example the ``ctslide`` format (for 
  presenting *concept test* questions) generates
  *multiple* slides: an initial *question* slide;
  an *answer* slide; and a slide enumerating the
  kinds of common errors people make on that question.

Easily Producing both a Homework and its Solutions Key
------------------------------------------------------

One nice benefit of this is that you can produce both
an assignment and its answer key by simply changing
the format from **question** to **answer**.


.. raw:: html

   <form id="build4" method="POST" action="/build_html">
   <input type="hidden" name="fname" value="basic4"/>
   <textarea cols=80 rows=12 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: Homework 4

   .. select:: mongodb:
      * summation_equalities_prob format=question
      * snp_detection_prob format=question
      * snp_scoring_pooled format=question
      * variable_ind_converse format=question

   </textarea>
   <input type="hidden" name="publicOnly" value="1"/>
   <BR>Make:
   <select name="outputFormat">
   <option value="html">web page</option>
   <option value="beamer">Slides</option>
   <option SELECTED value="latex">Document</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

Try this:

* First generate the homework assignment by making a Document
  (PDF) from the original version of this content.

* Next, change ``question`` to ``answer`` for all four selected
  items, and make a new Document (PDF).  This gives you a solution
  key!

* You can also try changing the formats to ``ctslide``, and make
  Slides.  This generates slides for you to present a question in
  class, then its answer.

Active Learning: Having Students Answer Questions In-Class
----------------------------------------------------------

A major focus of teachpub.org is making it easy for instructors
to incorporate active learning in their classes, in other words,
having students answer and discuss questions in class.
teachpub.org includes hundreds of *concept test* questions that
each probe understanding of a single concept.  Concept tests
involve a minimum of "mechanics": if you understand the concept,
you should be able to infer the answer simply by thinking
about how it applies to the question.  Students are given
a minute to think about the question, then enter their answers
using their laptop or smartphone (pointed at a teachpub.org
URL you give them; if your classroom lacks an internet
connection, you can instead run the "in-class question
system" on your own laptop connected to a cheap wifi router).
TeachPub.org uses the 
`Socraticqs <http://people.mbi.ucla.edu/leec/docs/socraticqs/>`_ 
In-Class Question System
to let you do all this very easily.  All you have to do
is choose the questions you want to ask.

This is illustrated by the following example:

.. raw:: html

   <form id="build5" method="POST" action="/build_html">
   <input type="hidden" name="fname" value="basic5"/>
   <textarea cols=80 rows=12 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: Conditional probability exercises

   .. select:: mongodb:
      * summation_equalities_prob format=ctslide
      * snp_detection_prob format=ctslide
      * snp_scoring_pooled format=ctslide
      * variable_ind_converse format=ctslide

   </textarea>
   <input type="hidden" name="publicOnly" value="1"/>
   <BR>Make:
   <select name="outputFormat">
   <option value="html">web page</option>
   <option value="beamer">Slides</option>
   <option value="latex">Document</option>
   <option SELECTED value="socraticqs">Socraticqs</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

* when you tell it to generate a Socraticqs class session,
  it will display a web page with links to both the instructor
  interface (which lets you walk the students step by step
  through whatever question(s) you want them to answer),
  and the student interface (which lets students answer
  the question(s) you assign them, self-evaluate what
  errors they made etc.).
* to try this out, first click the instructor interface link,
  and choose a question to ask the students.
* then click on the student interface link, click Register,
  and create a new student record.  You will then be shown
  the assigned question.
* back in the instructor interface, click the Go button
  (this simply starts a timer, that makes it convenient
  to see how long the exercise is taking).
* in the student interface, enter an answer.
* summary statistics for all student responses are updated
  every 15 seconds in the instructor interface.  You may
  also click the *show responses* link to display the 
  individual student answers.
* Typically, once more than half the students have answered,
  the instructor asks them to partner up with the person
  sitting next to them, and present their answers to each
  other (typically one minute each).  
* After a few minutes (whenever the instructor decides),
  the instructor presents the answer and usually asks
  the students to self-evaluate their answers and errors.
  To try this out, click the ASSESS link in the instructor
  interface; this starts the assessment phase.
* Back in the student interface, click ASSESS, and answer
  the questions on the assessment form.
* Again, the instructor can see updated statistics every
  15 seconds.
* Click SAVE to save all student response data to the 
  permanent database.

Searching TeachPub.org
----------------------

You can search all the content in teachpub.org.
This is illustrated by the following example:

.. raw:: html

   <form id="search" method="GET" action="/search">
   Search:
   <input type="text" name="query" size="40" maxlength="256" value="posterior"/>
   <BR>
   <select name="publicOnly">
   <option SELECTED value="1">Exclude private</option>
   <option value="0">Allow private</option>
   </select>
   questions (if you include private questions, you will be asked for a password). 
   <BR>
   <input type="submit"/>
   </form>


Formatting an exam with space for student answers
------------------------------------------------------

Templates permit you to control the details of the
formatting, for example, the amount of space to insert
for each question in an exam.  For example:

.. raw:: html

   <form id="build6" method="POST" action="/build_html">
   <input type="hidden" name="fname" value="basic6"/>
   <textarea cols=80 rows=12 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: Midterm Exam

   .. select:: mongodb:
      * summation_equalities_prob format=question insertPagebreak=1
      * snp_detection_prob format=question insertVspace=6cm
      * snp_scoring_pooled format=question insertPagebreak=1
      * variable_ind_converse format=question

   </textarea>
   <input type="hidden" name="publicOnly" value="1"/>
   <BR>Make:
   <select name="outputFormat">
   <option SELECTED value="latex">Document</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>


TeachPub.org Public vs. Secure Materials
----------------------------------------

When someone contributes a question to teachpub.org, they
may designate one of the following access policies:

* *public*: anyone can see the question and its answer.  Obviously,
  this makes sense for teaching materials, not for graded (test)
  questions.
* *answer-restricted*: the question, but not its answer, will be
  publicly accessible.  Authorized instructors can access the
  answer, and can use it in their courses, but should not post
  the answer publicly.
* *restricted*: the material is only accessible to
  authenticated instructors.  
* *final-exam-only*: instructors may only use in final exams,
  i.e. where no distribution of the question will ever occur,
  and no exposure of the answer.
* *private*: only the contributor can access the question
  (presumably to remix it with other materials on teachpub.org);
  later s/he may open it to other instructors.

Here's a simple example that illustrates how the teachpub.org
prototype already filters non-public material from its public
interface.  The first question is restricted-access; the second
is public:

.. raw:: html

   <form id="build7" method="POST" action="/build_html">
   <input type="hidden" name="fname" value="basic7"/>
   <textarea cols=80 rows=12 name="selectText">
   :Author: Christopher Lee
   :Organization: UCLA

   .. title:: Secure Materials Example

   .. select:: mongodb:
      * disease_test_condprob format=ctslide
      * NJ_connectivity format=ctslide

   </textarea>
   <BR>
   <select name="publicOnly">
   <option SELECTED value="1">Exclude private</option>
   <option value="0">Allow private</option>
   </select>
   questions (if you include private questions, you will be asked for a password). 
   <BR>Make:
   <select name="outputFormat">
   <option SELECTED value="html">web page</option>
   <option value="beamer">Slides</option>
   <option value="latex">Document</option>
   <option value="socraticqs">Socraticqs</option>
   </select>
   <input type="submit" value="Go!"/>
   </form>

Adding or Modifying "Units" in TeachPub.org
-------------------------------------------

We refer to an indivisible piece of
content (e.g. a multipart question, many of whose parts might not 
make sense without previous parts) as a "unit".  Units
are the basic building block that users edit or select from
the teachpub.org database.  Each unit will have its own
separate version control.

* units are written in the simple
  `reStructuredText <http://sphinx-doc.org/rest.html>`_ format,
  which can be automatically intercoverted from / to any
  standard format.

* *metadata*: units in teachpub.org are extensively annotated
  with metadata that link them to each other and to external
  resources.  Specifically, a series of standard predicates
  (defines, tests, motivates, derives, illustrates, etc.) links each
  unit to Wikipedia concept IDs.  Hence the content in TeachPub.Net
  can be considered a *concept graph* whose nodes are Wikipedia
  concept IDs, and whose edges are units that relate one concept
  to another in a specified way.  E.g. the Monty Hall problem
  illustrates an example of Bayes' Law.  Initially, this enables 
  TeachPub.Net to provide links to Wikipedia; many other applications
  are possible.

Here's a simple example::

    :question: disease_test_condprob
      :title: Disease Test Question
      :tests: Disease_test_example
      A biotech company has developed a
      new test for a rare disease (found in less than 1% of the population),
      which predicts either that a patient has or
      does not have the disease.
      The company reports that in a random patient sample
      the test was 97% accurate (i.e. gave a negative test result)
      among patients who did not have the disease, 
      and 95% accurate (positive test result)
      among patients who actually had the disease.
      Choose the statement that best characterizes the test's reliability
      for a patient trying to interpret his test result.
      :multichoice:
        * The test reliably indicates whether the patient has disease or not.
        * The test does not reliably indicate whether the patient has
          disease or not.
        * The test's reliability depends on whether the test result is
          positive or negative. :correct:
        * The test's reliability depends on whether the patient
          has disease or not.
        * There's no way to know, based on this information.
      :answer:


        * This question asked you to assess the conditional probability
          :math:`p(D|T)`.  I.e. given the observation (the test result),
          what is the reliability vs. uncertainty in forecasting the hidden
          variable (whether the patient has disease).

        * Note that the question gave you the converse conditional probabilities
          :math:`p(T|D)`.  These are not relevant to a patient or doctor because
          they do not go from "what you know" (:math:`T`)
          to "what you want to know" (:math:`D`).

        * Estimating :math:`p(D^+|T^+)` follows straight from the stated numbers:
          :math:`p(D^+,T^+)<1\%`, and :math:`p(D^-, T^+)=3\%`, so
          :math:`p(D^+|T^+)<25\%`.  Not very reliable!
    
        * This problem of high false positive rate (because the actual disease
          is rare) is a very common problem in bioinformatics, where our calculations
          must "scale", e.g. to search for a single disease gene out of the 
          entire genome of 25,000 genes.

      :error:
        Many people didn't consider the *direction* of the conditional
        probability, even though the question's phrasing and answers encouraged
        you to do that.  (The question
        gave you :math:`p(O|H)` but asked you about :math:`p(H|O)`).
        Implies they didn't realize that any conditional
        probability has two possible directions.
      :error:
        In particular, people often forget to ask themselves which 
        direction is relevant in real life, i.e. which variable is
        *hidden* vs. *observable*.
        Suggestion: remember we can only make inferences (calculate
        probabilities) of things we want to know (*hidden*) based on
        things we know (observable).
        Etch into your minds: *Which variable is hidden? Which varible is
        observed?  Which direction of conditional probability am I being asked for?*
      :error:
        Etch into your minds: if a (hidden) state is rare, be very worried
        about the false positive rate (no matter how good the test is)!!
      :error:
        Some people chased red herrings like "does *reliable* mean 95%? 97%?"

Error Models in TeachPub.org
----------------------------

The example above illustrates an important principle.
TeachPub.org includes both *solutions* and *error models*
for most problems.  *Error models* are a categorization of 
distinct conceptual misunderstandings that students
make on each of these problems, i.e. not the (surface) discrepancy
vs. the correct answer, but its root cause.  These represent the
key ways in which a class "loses" its students (i.e. they misunderstand
an important aspect of a concept).

In our view this is a good
example of how shared teaching materials can be better than
"private" teaching materials.  Textbooks simply do not 
undertake this kind of analysis.  Instructors likewise do not
see the wide range of error models on each concept unless
they actually run concept tests in every class session and
read all the student answers.  Even if they do, that information
is simply lost, i.e. it does not propagate to other
instructors.  Students themselves often don't
realize they've misunderstood, or cannot put a finger on exactly
where they went wrong (and hence cannot fix it).
By contrast, in a shared teaching materials repository,
faculty can each easily add error models they've observed
for a given question.  Not only will all users of that question
see these error models (and can address them in their teaching),
the Socraticqs in-class question system (see below) will automatically 
ask students answering this question whether they made any of
these known, common errors (and if they think they made a novel
error can flag their answer for further analysis by instructors).  
Identifying an individual student's error model could
be automatically linked to appropriate review and follow-up
exercises to correct the error, giving the student in effect
a custom tutorial tailored to their individual understanding.
Error models in the initial teachpub.org dataset 
have been derived from sample sizes
of 25 - 100 student answers per question.

