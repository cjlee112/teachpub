import cherrypy
import thread
import subprocess
from reusabletext import mongo, parse, ctprep, vanilla
from socraticqs import question
import socraticqs.web
import json
import os.path
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


class Server(object):
    def __init__(self, sourceDir="sphinx_source", 
                 buildDir='staticroot/docs', docIndex=None, formatIndex=None,
                 noCachePragma=''):
        #if not docIndex:
        #    docIndex = mongo.DocIDIndex()
        #if not formatIndex:
        #    formatIndex = mongo.FormatIndex()
        #self.docIndex = docIndex
        #self.formatIndex = formatIndex
        self.sourceDir = sourceDir
        self.buildDir = buildDir
        self.latexDocs = {}
        self.coll = mongo.get_collection()
        formatDict = parse.read_formats('vanilla_formats.rst')
        self.reformatter = vanilla.Reformatter(formatDict)
        self.noCachePragma = noCachePragma
        self.course = {}

    def start(self):
        'start cherrypy server as background thread, retaining control of main thread'
        self.threadID = thread.start_new_thread(self.serve_forever, ())

    def serve_forever(self):
        cherrypy.quickstart(self, '/', 'cp.conf')

    def build_html(self, fname, selectText, outputFormat='html'):
        rawtext = selectText.split('\n')
        stree = parse.parse_rust(rawtext, fname)
        usePDFpages = ctprep.check_fileselect(stree)
        parse.apply_select(stree)
        if outputFormat == 'socraticqs':
            return self.init_socraticqs(fname, stree)
        path = os.path.join(self.sourceDir, fname + '.rst')
        with open(path, 'w') as ofile:
            ofile.write(self.noCachePragma)
            ofile.write(parse.get_text(stree))
        if outputFormat == 'beamer':
            texfile = ctprep.make_tex(path, usePDFpages) # run rst2beamer
            subprocess.call(['pdflatex', '-output-directory', 
                             self.buildDir, '-interaction=batchmode',
                             texfile])
            return redirect('/docs/%s.pdf' % fname)
        elif outputFormat == 'latex': # add to sphinx conf.py latexdocs
            self.latexDocs[fname] = (fname, fname + '.tex', 'The Title',
                                     'the Author', 'howto')
            with open(os.path.join(self.sourceDir, 'latexdocs.json'), 
                      'w') as ifile:
                json.dump(self.latexDocs, ifile)

        cmdline.main(['sphinx-build', '-b', outputFormat,
                      self.sourceDir, self.buildDir, 
                      path]) # build desired output via sphinx
        if outputFormat == 'html':
            return redirect('/docs/%s.html' % fname)
        elif outputFormat == 'latex': # need to run pdflatex
            texfile = os.path.join(self.buildDir, fname + '.tex')
            subprocess.call(['pdflatex', '-output-directory', 
                             self.buildDir, '-interaction=batchmode',
                             texfile])
            return redirect('/docs/%s.pdf' % fname)
    build_html.exposed = True

    def search(self, query):
        l = mongo.text_search(self.coll, query, limit=100)
        searchDocs = [t[0] for t in l]
        outfile = os.path.join(self.sourceDir, 'results.rst')
        vanilla.render_docs(searchDocs, self.reformatter, outfile,
                            self.noCachePragma + '''
**Search results: %d documents** (click on titles shown on the left
to jump to a specific document)

''' % len(searchDocs))
        cmdline.main(['sphinx-build',  # build desired output via sphinx
                      self.sourceDir, self.buildDir, outfile])
        return redirect('/docs/results.html')
    search.exposed = True
    
    def init_socraticqs(self, fname, stree):
        #qlist = setup_questions(stree)
        qset = ctprep.get_questions(stree)
        ctprep.save_question_csv(qset, fname + '.csv', parse.PostprocDict,
                                 '/staticroot/images')
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
        return redirect('/docs/test.html') # test form for instructors
    index.exposed = True

            


if __name__ == '__main__':
    s = Server()
    print 'starting server...'
    s.start()


