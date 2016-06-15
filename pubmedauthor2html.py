#!/usr/bin/env python
#   Simple script to query pubmed for a DOI
#   (c) Simon Greenhill, 2007
#   http://simon.net.nz/
#
# Modified by Matt Huska, 2016
# Search by author and return all papers in a styled html format

import urllib
from xml.dom import minidom

def get_articles_from_search(query, params):
    params['term'] = query
    # try to resolve the PubMed ID of the DOI
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.urlencode(params)
    data = urllib.urlopen(url).read()
    # parse XML output from PubMed...
    xmldoc = minidom.parseString(data)
    ids = xmldoc.getElementsByTagName('Id')
    # nothing found, exit
    if len(ids) == 0:
        raise "DoiNotFound"
    return ids

def get_data_for_id(id, params):
    params['id'] = id
    params['retmode'] = 'xml'
    # get citation info:
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.urlencode(params)
    data = urllib.urlopen(url).read()
    return data

def text_output(xml):
    """Makes a simple text output from the XML returned from efetch"""
    xmldoc = minidom.parseString(xml)
    title = xmldoc.getElementsByTagName('ArticleTitle')[0]
    title = title.childNodes[0].data
    abstract = xmldoc.getElementsByTagName('AbstractText')[0]
    abstract = abstract.childNodes[0].data
    authors = xmldoc.getElementsByTagName('AuthorList')[0]
    authors = authors.getElementsByTagName('Author')
    authorlist = []
    for author in authors:
        LastName = author.getElementsByTagName('LastName')[0].childNodes[0].data
        Initials = author.getElementsByTagName('Initials')[0].childNodes[0].data
        author = '%s, %s' % (LastName, Initials)
        authorlist.append(author)
    journalinfo = xmldoc.getElementsByTagName('Journal')[0]
    journal = journalinfo.getElementsByTagName('Title')[0].childNodes[0].data
    journalinfo = journalinfo.getElementsByTagName('JournalIssue')[0]
    #volume = journalinfo.getElementsByTagName('Volume')[0].childNodes[0].data
    #issue = journalinfo.getElementsByTagName('Issue')[0].childNodes[0].data
    year = journalinfo.getElementsByTagName('Year')[0].childNodes[0].data
    # this is a bit odd?
    #pages = xmldoc.getElementsByTagName('MedlinePgn')[0].childNodes[0].data
    ids = xmldoc.getElementsByTagName('ArticleIdList')[0]
    ids = ids.getElementsByTagName('ArticleId')
    pmid=""
    doi=""
    for id in ids:
        #print id.toxml()
        attr = id.getAttribute("IdType")
        if attr == 'doi':
            doi = id.firstChild.data
        elif attr == "pubmed":
            pubmed = id.firstChild.data

    #doi = xmldoc.getElementsByTagName('doi')[0].childNodes[0].data
    #pmid = xmldoc.getElementsByTagName('pubmed')[0].childNodes[0].data

    output = []
    output.append(', '.join(authorlist))
    output.append(title)
    #output.append( '%s %s, %s (%s):%s' % (journal, year, volume, issue, pages) )
    output.append( '%s %s' % (journal, year) )
    # details: http://www.ncbi.nlm.nih.gov/books/NBK3862/
    # example: http://www.ncbi.nlm.nih.gov/pubmed/18276894
    output.append( 'PMID: <a href="http://www.ncbi.nlm.nih.gov/pubmed/%s">%s</a> doi:%s' % (pmid, pmid, doi) )

    #output.append(title)
    #output.append('') #empty line
    #output.append(', '.join(authorlist))
    #output.append( '%s %s, %s (%s):%s' % (journal, year, volume, issue, pages) )
    #output.append('') #empty line
    #output.append(abstract)

    return output

if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) == 1:
        print 'Usage: %s <query>' % argv[0]
        print ' e.g. %s 10.1038/ng1946' % argv[0]
        exit()

    params = {
            'db':'pubmed',
            'tool':'pubmedauthor2html',
            'email':'huska@molgen.mpg.de',
            'usehistory':'y',
            'retmax':20
            }

    ids = get_articles_from_search(argv[1], params)
    params.pop('usehistory')
    params.pop('retmax')

    for iddom in ids:
        id = iddom.childNodes[0].data
        data = get_data_for_id(id, params)
        print '. '.join(text_output(data))


