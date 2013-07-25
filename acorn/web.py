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
import Queue


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

def build_docs(srcdir='../sitedocs', destdir='staticroot/docs'):
    subprocess.call(['sphinx-build', '-b', 'html', srcdir, destdir])


class Server(object):
    def __init__(self, sourceDir="sphinx_source", 
                 buildDir='staticroot/remix', docIndex=None, formatIndex=None,
                 noCachePragma='', imageDir='sphinx_source', 
                 privateDir='staticroot/private', maxUser=100,
                 startPage='/docs/index.html', **kwargs):
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
        self.idQueue = Queue.Queue() # thread-safe container
        self.maxUser = maxUser
        self.load_userID()

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

    def load_userID(self):
        for i in range(self.maxUser):
            self.idQueue.put(i)

    def next_userID(self):
        while True:
            try:
                return self.idQueue.get_nowait()
            except Queue.Empty:
                self.load_userID()

    def session_userID(self):
        'get userID for this session, or allocate one if needed'
        try:
            return cherrypy.session['userID']
        except KeyError:
            userID = self.next_userID()
            cherrypy.session['userID'] = userID
            return userID

    def build_html(self, fname, selectText, outputFormat='html', publicOnly=1,
                   beamerTheme=None, docTitle='My Presentation', 
                   author='the Author'):
        userID = self.session_userID()
        fname = '%s_%d' % (fname, userID)
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
            if publicOnly:
                secure_questions(stree) # remove non-public questions
            return self.init_socraticqs(fname, stree, publicOnly)
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
            subprocess.call(['sphinx-build', '-b', outputFormat,
                             self.sourceDir, texDir, 
                             path]) # build latex
            pdflatex(texDir, fname, outputDir)
            return redirect('/%s/%s.pdf' % (webroot, fname))
        elif outputFormat == 'html':
            subprocess.call(['sphinx-build', '-b', outputFormat,
                             self.sourceDir, outputDir, 
                             path]) # build html
            return redirect('/%s/%s.html' % (webroot, fname))
        else:
            raise ValueError('unknown format: ' + outputFormat)
    build_html.exposed = True

    def search(self, query, publicOnly=1, fname='results'):
        userID = self.session_userID()
        fname = '%s_%d' % (fname, userID)
        publicOnly = int(publicOnly)
        l = mongo.text_search(self.coll, query, limit=100)
        searchDocs = [t[0] for t in l]
        if publicOnly:
            searchDocs = filter(is_public, searchDocs)
        outfile = os.path.join(self.sourceDir, fname + '.rst')
        vanilla.render_docs(searchDocs, self.reformatter, outfile,
                            self.noCachePragma + '''
**Search results: %d documents** (click on titles shown on the sidebar
to jump to a specific document)

''' % len(searchDocs))
        outputDir = self.get_output_dir(publicOnly)
        webroot = os.path.basename(outputDir)
        subprocess.call(['sphinx-build',  # build desired output via sphinx
                         self.sourceDir, outputDir, outfile])
        return redirect('/%s/%s.html' % (webroot, fname))
    search.exposed = True
    
    def init_socraticqs(self, fname, stree, publicOnly=True):
        #qlist = setup_questions(stree)
        qset = ctprep.get_questions(stree)
        ctprep.save_question_csv(qset, fname + '.csv', parse.PostprocDict,
                                 'staticroot/images', self.imageDir)
        adminIP = cherrypy.request.remote.ip
        cherrypy.session['courseID'] = fname
        dbfile = fname + '.db'
        if publicOnly:
            rootPath = '/socraticqs'
        else:
            rootPath = '/socraticqsp'
        socServer = socraticqs.web.Server(fname + '.csv', adminIP=adminIP,
                                          configPath=None, mathJaxPath=None,
                                          dbfile=dbfile, rootPath=rootPath,
                                          shutdownFunc=self.end_socraticqs)
        socServer._teachpub_fname = fname
        self.course[fname] = socServer
        return '''<H1>Socraticqs Demo</H1>%d concept tests loaded.  
<H2>Demo Instructions</H2>
<LI>Click here to launch the 
<A HREF="%s/admin" TARGET="admin">instructor interface</A>
in a separate window.</LI>
<LI>Click on a question to assign it to the class.</LI>
<LI>In a real class, you would explain the question to the students,
then click <B>Go</B> to start the answer period.</LI>
<LI>Click here to launch the 
<A HREF="%s/index" TARGET="student">student interface</A>
in a separate window.</LI>
<LI>Click the <B>Register</B> link to add a new student.
You can enter any values you want for the student username, full name,
and UID.</LI>
<LI>Use the student interface to answer the question; use
the instructor interface to watch the student's answer appear, etc.</LI>
<LI>When your Socraticqs demo session is finished, close
the instructor and student interface windows.  You may click your
browser's Back button in this window to go back to your TeachPub page.</LI>

An <A HREF="http://people.mbi.ucla.edu/leec/docs/socraticqs/" TARGET="socdocs">
overview and complete documentation</A> of Socraticqs is available
here.
''' % (len(qset.children), rootPath, rootPath)

    def end_socraticqs(self, socServer, msg):
        del self.course[socServer._teachpub_fname] # disconnect server
        return '''Your Socraticqs session is ended.  Close this tab to
return to your TeachPub page.'''

    def socraticqs(self, *args, **kwargs):
        'pass requests to socraticqs server'
        try:
            s = self.course[cherrypy.session['courseID']]
        except KeyError:
            return redirect(self.startPage, 
                            '''The instructor has closed this Socraticqs 
session.  Returning to TeachPub homepage in 10 seconds...''', 10)
        try:
            m = args[0]
        except IndexError:
            m = 'index'
        return getattr(s, m)(**kwargs) # call socraticqs method
    socraticqs.exposed = True
        
    def socraticqsp(self, *args, **kwargs):
        'stub for private socraticqs interface'
        return self.socraticqs(*args, **kwargs)
    socraticqsp.exposed = True


    def index(self, **kwargs):
        userID = self.session_userID() # immediately assign session userID
        return redirect(self.startPage)
    index.exposed = True

            


if __name__ == '__main__':
    try:
        with open('data.json') as ifile:
            d = json.load(ifile)
        kwargs = dict(host='mongodb://%(user)s:%(password)s@%(host)s/%(dbName)s'
                      % d, port=d['port'], dbName=d['dbName'])
    except IOError:
        kwargs = {}

    build_docs()
    s = Server(**kwargs)
    print 'starting server...'
    s.start()


