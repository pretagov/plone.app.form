from zope import interface, schema
from zope.component import getMultiAdapter, provideAdapter
from zope.formlib import form
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app.form.browser.interfaces import ISourceQueryView, ITerms
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.source import SourceInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.CMFCore import utils as cmfutils
from Products.Five.browser import pagetemplatefile

from pprint import pprint

class IUberSelect(interface.Interface):
    pass


class UberSelect(schema.Choice):
    interface.implements(IUberSelect)


class MySource(object):
    interface.implements(schema.interfaces.ISource)

    def __contains__(value):
        """Return whether the value is available in this source
        """
        return False


class MyTerms(object):
    interface.implements(ITerms)

    def __init__(self, source, request):
        pass # We don't actually need the source or the request :)

    def getTerm(self, value):
        title = unicode(value)
        try:
            token = title.encode('base64').strip()
        except binascii.Error:
            raise LookupError(token)
        return schema.vocabulary.SimpleTerm(value, token=token, title=title)

    def getValue(self, token):
        return token.decode('base64')

provideAdapter(
    MyTerms,
    (MySource, IBrowserRequest)
)


class QuerySchemaSearchView(object):
    interface.implements(ISourceQueryView)

    template = ViewPageTemplateFile('uberselectionwidget.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self, name):
        return None

    def results(self, name):
        if not name+".search":
            return None
        query_fieldname = name+".query"
        if query_fieldname in self.request.form:
            query = self.request.form[query_fieldname]
            if query != '':
                return ('spam', 'spam', 'spam', 'ham', 'eggs')
            else:
                return None
        else:
            return None

provideAdapter(
    QuerySchemaSearchView,
    (MySource, IBrowserRequest)
)


class IUberSelectionDemoForm(interface.Interface):
    text = UberSelect(title=u'Search Text',
                         description=u'The text to search for',
                         required=False,
                         source=MySource())


class UberSelectionWidget(SourceInputWidget):
    template = ViewPageTemplateFile('uberselectionwidget.pt')

    def queryviews(self):  
        return [
                    (self.name,
                     getMultiAdapter(
                        (self.source, self.request),
                        ISourceQueryView,
                     )
                    )
               ]

    queryviews = property(queryviews)
            
    def __call__(self):
        value = self._value()
        field = self.context
        results = []
        for name, queryview in self.queryviews:
            qresults = queryview.results(name)
            if qresults is not None:
                for item in qresults:
                    results.append(self.terms.getTerm(item))
        return self.template(field=field, results=results, name=self.name)


class UberSelectionDemoForm(form.PageForm):
    form_fields = form.FormFields(IUberSelectionDemoForm)

    @form.action("dskljfhsd")
    def action_search(self, action, data):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')

        return repr(data)
