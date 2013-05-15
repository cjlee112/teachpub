#######################
TeachSource Design v0.1
#######################

Components of a basic scrubjay website
--------------------------------------

* content in mongodb: DONE
* select from mongodb: DONE
* db stores both source and tree for each record
* extend SELECT to mongo ID
* store SELECT source in db ("assemblies")
* output compilers:

  * HTML (via Sphinx): DONE
  * beamer (via rst2beamer): DONE
  * latex (via Sphinx): DONE
  * socraticqs: DONE

* edit / save your own assemblies
* search, browse units and assemblies from db

  * should probably change text storage to a single
    string via '\n'.join(text), and convert
    back to list on extraction via s.split('\n').
  * then we can use the new mongodb 2.4 text search index
    feature.  Need to turn text indexing on, and 
    add such an index to our collection.
  * then search via::

      db.command('text', 'latest', search='some text search')
  
    where db is pymongo socraticqs database object, and 'latest' is
    name of our collection.
  * we get back a bunch of matching records, show them to
    the user, let him copy _id to his select statements.


Questions
---------

* do we need "human-readable" IDs anymore?  Seems like just
  a flaw of the previous design (which lacked a real database and unique IDs)

Output compilation
------------------

* get a tree containing SELECT
* run parse.get_text() and write string output to file
* run ctprep.make_tex() to produce tex via rst2beamer
* run pdflatex on the tex file
* download to the user

To build with sphinx:

from sphinx import cmdline
cmdline.main(argv) # include filename target





website design steps
--------------------

Two separate pieces of this

* put socraticqs on the web, make it multiclass: fairly easy...
* teaching materials database and "mashup" website: harder...

* import RUsT into mongodb
* adapt select / templating mechanism to use content from mongodb
* need to define "unit" vs. "structure"
* browse materials and mark what looks interesting
  * use someone else's structure
  * make your own structure
  * (edit a unit)

what goes in the repository?

* the easy part: a unit -- just RUsT parse tree
  * each Section becomes separate db record
  * question Block becomes separate db record.  Consider grouping
    questions under Section that defines concept that each question
    tests, same as we do for other Block (e.g. comment).

* the hard part: assemblies.  You could start with my existing
  select syntax and try to improve on it later...  The current
  syntax gets the job done.  The only extension I'd suggest now
  is allowing recursion (i.e. assembly of assemblies).  The
  difference between unit and assembly is that assembly has
  to be "compiled" to produce ReST output.  This becomes
  like a Makefile: we recompile when our dependencies change.

Look at ways to interface this with iPython?

advantages of the parse tree database
-------------------------------------

* trivial issues like indentation are eliminated.
* db gives us real IDs automatically.
* do diff / patch on the tree structure rather than flat text
* the database is queryable, unlike a Pickle representation...
* definitely do not use an SQL schema... schema is sure to
  change or vary between the needs of different applications.

Do we split content into more than one collection?

How is versioning going to be handled in this construct?
Reference will either be to 

At the assembly level it makes sense to commit a snapshot
of the exact version of all the inputs to your assembly.
Basically, when you compile a product.

What to store:

* main record stores

  * HEAD text for searching
  * HEAD parsetree
  * HEAD metadata
  * HEAD owner
  * list of authors

    * list of branches, each points to a commit

* commit collection
* tree collection
* blob collection

easiest to follow the git model for storing these data.

For v1, don't implement version control.


The Powerpoint (source code) conundrum
--------------------------------------

how to deal with the fact almost everyone else in the
universe will be editing Powerpoint and Word files?
(or even worse, Keynote and Pages documents)?

* to begin with you can pull individual slides via the pdf mechanism
* better to extract the basic content (source text), store in db
* PP etc. become just another compiled format target.

ReST is plain content without style information.  On the one hand
that makes it easily reusable (the output format re-styles it
appropriately), but on the other hand I've mostly ignored the
whole question of controlling style and format.  I think it's
right to separate content and style,
and remix them at the output compilation stage.  At the moment
the select directive is the place where that happens (through
named templates).  I think that's the right basic idea, but of 
course extraordinarily limited in its current form.

We need a much simpler "transformations" framework than
docutils.  Docutils is too cumbersome and opaque; its limited
utility doesn't justify its complexity. 

Instead work with a pure
structural representation (basically the parse tree) and
only "compile" it to a specific rendering language at
the output stage.

All this just says: for the moment, stay close to what you've
already got, because it works.  Later, people can improve on this
in all sorts of ways, but right now it'd be a mistake trying to
solve all sorts of future needs that we don't even understand yet.

Mashup interface
----------------

Typically you're editing an assembly, which involves

* adding or removing units
* re-ordering units
* choosing or adjusting unit format, parameters

You can imagine this would consist of draggable divs containing
rendered content.  You could click a unit to edit it (if source
code available).

Finally you choose an output format to compile, e.g.
slides.

Security
--------

Once you direct students to log in to your site, the
university will feel you are "stealing their confidential data".
Options:

* only handle *ungraded* exercises.  Graded materials must be
  handled by the instructor or transferred to the university's
  systems (e.g. Moodle).  This is sensible.  Having students
  do graded work online is almost begging them to cheat
  (i.e. Google for the answer)...
* encrypt all student data with instructor's public key; 
  instructor downloads and decrypts.
* student ID numbers might be considered to be confidential.
  So you may have to use something public such as email address
  as the student identifier.

Version Control
---------------

the crucial requirement is automatic merging of separate sets of diffs.
(fast-forward is trivial).


How to store parsetree?
-----------------------

options

* ReST text
* RUsT primitives

  * section (container): with metadata
  * block (container): with metadata
  * text: containing markup bound to intervals. Implement as 
    block with no children.

  * list (numbering optional).  Implement as block whose items
    are its children.

  * table: Implement same as list, but expect each top-level
    item itself to be a list.

  * directive: default is just to store its raw content.
    but can define subclass that preprocesses content to store whatever
    it wants.

metadata are just strings.

block by contrast is a subtree.

looks like jsonpickle would be a good way to persist these.


