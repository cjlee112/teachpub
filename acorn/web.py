import cherrypy
import thread
import subprocess
from reusabletext import mongo, parse, ctprep, vanilla
from socraticqs import question
import socraticqs.web
import json
import os.path
import tempfile
import shutil
try:
    from sphinx import cmdline
except ImportError:
    pass


def redirect(path='/', body=None, delay=0):
    'redirect browser, if desired after showing a message'
    s = '<HTML><HEAD>\n'
    s += '<meta http-equiv="Refresh" content="%d; url=%s">\n' % (delay, path)
    s += '</HEAD>\n'
    if body:
        s += '<BODY>%s</BODY>\n' % body
    s += '</HTML>\n'
    return s


def setup_questions(tree):
    qSet = ctprep.get_questions(tree)
    l = []
    for t in ctprep.generate_question_attrs(qSet, postprocDict, 
                                            imageFiles):
        qtype, title, text, answer, errorModels = t[:5]
        if qtype == 'mc':
            correct, choices = t[5:]
            args = tuple(errorModels) + (correct,) + tuple(choices)
            qObj = question.QuestionChoice(id, title, text, answer,
                                           len(errorModels), *args)
        else:
            qObj = question.QuestionText(id, title, text, answer,
                                         len(errorModels), *errorModels)
        l.append(qObj)
    return l

unauthorizedQ = '''

Unauthorized Request
--------------------

You have requested a question that is not publicly accessible
but have not authenticated your identity.
'''

def is_public(c):
    return getattr(c, 'tokens', ('skip',))[0] != ':question:' \
        or 'public' in getattr(c, '_metadata', {}).get('access', ())

def secure_questions(tree, publicOnly=True, replaceText=unauthorizedQ):
    nonpublic = 0
    for i,c in enumerate(tree.children):
        if getattr(c, 'tokens', ('skip',))[0] != ':question:': # filter subtree
            nonpublic += secure_questions(c, publicOnly, replaceText)
        elif hasattr(c, 'selectParams') \
               and 'public' not in getattr(c, '_metadata', {}) \
               .get('access', ()):
            nonpublic += 1 # count non-public questions
            if publicOnly: # block access
                print 'block access, publicOnly=%d' % publicOnly
                rtree = parse.parse_rust(replaceText.split('\n'), 'temp')
                tree.children[i] = rtree.children[0]
    return nonpublic

def cprmtemp(srcdir, fname, destdir):
    'copy file to dest and remove srcdir'
    shutil.copyfile(os.path.join(srcdir, fname), os.path.join(destdir, fname))
    shutil.rmtree(srcdir)

def pdflatex(srcdir, fname, destdir):
    'run pdflatex with tempdir to prevent nasty side effects'
    tempDir = tempfile.mkdtemp()
    subprocess.call(['pdflatex', '-output-directory', tempDir,
                     '-interaction=batchmode', fname + '.tex'], cwd=srcdir)
    cprmtemp(tempDir, fname + '.pdf', destdir)

def build_livetutorial(srcdir, destdir):
    cmdline.main(['sphinx-build', '-b', 'html', srcdir, destdir])


class Server(object):
    def __init__(self, sourceDir="sphinx_source", 
                 buildDir='staticroot/docs', docIndex=None, formatIndex=None,
                 noCachePragma='', imageDir='sphinx_source', 
                 privateDir='staticroot/private', 
                 liveTutorial='../livetutorial', 
                 startPage='/docs/tutorial/basic.html', **kwargs):
        if not docIndex:
            docIndex = mongo.DocIDIndex(**kwargs)
        if not formatIndex:
            formatIndex = mongo.FormatIndex(**kwargs)
        self.docIndex = docIndex
        self.formatIndex = formatIndex
        self.sourceDir = sourceDir
        self.buildDir = buildDir
        self.privateDir = privateDir
        self.imageDir = imageDir
        self.startPage = startPage
        self.latexDocs = {}
        self.coll = mongo.get_collection(**kwargs)
        formatDict = parse.read_formats('vanilla_formats.rst')
        self.reformatter = vanilla.Reformatter(formatDict)
        self.noCachePragma = noCachePragma
        self.course = {}
        if liveTutorial:
            build_livetutorial(liveTutorial, 
                               os.path.join(buildDir, 'tutorial'))

    def start(self):
        'start cherrypy server as background thread, retaining control of main thread'
        self.threadID = thread.start_new_thread(self.serve_forever, ())

    def serve_forever(self):
        cherrypy.quickstart(self, '/', 'cp.conf')

    def get_output_dir(self, publicOnly):
        if publicOnly:
            return self.buildDir
        else:
            return self.privateDir

    def build_html(self, fname, selectText, outputFormat='html', publicOnly=1,
                   beamerTheme=None, docTitle='My Presentation', 
                   author='the Author'):
        publicOnly = int(publicOnly)
        rawtext = selectText.split('\n')
        stree,t,a = parse.parse_rust_docinfo(rawtext, fname, 
                                             mongoIndex=self.docIndex,
                                             mongoFormats=self.formatIndex)
        if t:
            docTitle = t
        if a:
            author = a
        usePDFpages = ctprep.check_fileselect(stree)
        parse.apply_select(stree)
        if outputFormat == 'socraticqs':
            secure_questions(stree, True) # remove non-public questions
            return self.init_socraticqs(fname, stree)
        nonpublic = secure_questions(stree, publicOnly)
        outputDir = self.get_output_dir(publicOnly or nonpublic == 0)
        outputDir = os.path.abspath(outputDir)
        webroot = os.path.basename(outputDir)
        path = os.path.join(self.sourceDir, fname + '.rst')
        with open(path, 'w') as ofile:
            ofile.write(self.noCachePragma)
            ofile.write(parse.get_text(stree))
        if outputFormat == 'beamer': # run rst2beamer
            ctprep.make_tex(path, usePDFpages, beamerTheme, docTitle)
            pdflatex(self.sourceDir, fname, outputDir)
            return redirect('/%s/%s.pdf' % (webroot, fname))
        elif outputFormat == 'latex': # add to sphinx conf.py latexdocs
            self.latexDocs[fname] = (fname, fname + '.tex', docTitle,
                                     author, 'howto')
            with open(os.path.join(self.sourceDir, 'latexdocs.json'), 
                      'w') as ifile:
                json.dump(self.latexDocs, ifile)
            texDir = os.path.join(self.sourceDir, '_build', 'latex')
            cmdline.main(['sphinx-build', '-b', outputFormat,
                          self.sourceDir, texDir, 
                          path]) # build latex
            pdflatex(texDir, fname, outputDir)
            return redirect('/%s/%s.pdf' % (webroot, fname))
        elif outputFormat == 'html':
            cmdline.main(['sphinx-build', '-b', outputFormat,
                          self.sourceDir, outputDir, 
                          path]) # build html
            return redirect('/%s/%s.html' % (webroot, fname))
        else:
            raise ValueError('unknown format: ' + outputFormat)
    build_html.exposed = True

    def search(self, query, publicOnly=1):
        publicOnly = int(publicOnly)
        l = mongo.text_search(self.coll, query, limit=100)
        searchDocs = [t[0] for t in l]
        if publicOnly:
            searchDocs = filter(is_public, searchDocs)
        outfile = os.path.join(self.sourceDir, 'results.rst')
        vanilla.render_docs(searchDocs, self.reformatter, outfile,
                            self.noCachePragma + '''
**Search results: %d documents** (click on titles shown on the left
to jump to a specific document)

''' % len(searchDocs))
        outputDir = self.get_output_dir(publicOnly)
        webroot = os.path.basename(outputDir)
        cmdline.main(['sphinx-build',  # build desired output via sphinx
                      self.sourceDir, outputDir, outfile])
        return redirect('/%s/results.html' % webroot)
    search.exposed = True
    
    def init_socraticqs(self, fname, stree):
        #qlist = setup_questions(stree)
        qset = ctprep.get_questions(stree)
        ctprep.save_question_csv(qset, fname + '.csv', parse.PostprocDict,
                                 'staticroot/images', self.imageDir)
        adminIP = cherrypy.request.remote.ip
        cherrypy.session['courseID'] = fname
        dbfile = fname + '.db'
        self.course[fname] = socraticqs.web.Server(fname + '.csv',
                                                   adminIP=adminIP,
                                                   configPath=None,
                                                   mathJaxPath=None,
                                                   dbfile=dbfile)
        return '''%d concept tests loaded.  Click here to launch the 
<A HREF="/admin" TARGET="admin">instructor interface</A>.
Click here to launch the 
<A HREF="/" TARGET="student">student interface</A>. 
''' % len(qset.children)
        
    # forward the socraticqs web interface calls
    socraticqsMethods = ('login', 'login_form', 'logout',
                         'register_form', 'register', 'reconsider_form',
                         'view', 'submit', 'admin', 'start_question',
                         'qadmin', 'qassess', 'save_responses', 'exit')
    for attr in socraticqsMethods:
        exec '''%s=lambda self, **kwargs:self.call_socraticqs("%s", **kwargs)
%s.exposed = True''' % (attr, attr, attr)
    del socraticqsMethods, attr # don't leave clutter in class attributes

    def call_socraticqs(self, m, **kwargs):
        courseID = cherrypy.session['courseID']
        return getattr(self.course[courseID], m)(**kwargs)

    def index(self, **kwargs):
        if 'courseID' in cherrypy.session: # student interface
            return self.call_socraticqs('index', **kwargs)
        return redirect(self.startPage) # test form for instructors
    index.exposed = True

            


if __name__ == '__main__':
    s = Server()
    print 'starting server...'
    s.start()


