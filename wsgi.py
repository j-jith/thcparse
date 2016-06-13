#!/usr/bin/env python
import os
from lxml import etree
import re
from cgi import parse_qs, escape
#import StringIO

from xpf_module import generate_xpf
from ipuz_module import generate_ipuz
from puz_module import generate_puz

#import bjoern # for local testing

def application(env, start_response):
    if 'QUERY_STRING' in env:
        queries = parse_qs(env['QUERY_STRING'])
    else:
        queries = None

    if queries:
        xwd_url = escape(queries.get('xwd_url')[0])
        xwd_format = escape(queries.get('format')[0])
    else:
        xwd_url = None
        xwd_format = None
    
    if xwd_url and xwd_format:
        if xwd_format == 'ipuz':
            ctype = 'application/json'
            [filecontent, filename] = generate_ipuz(xwd_url)
            #filelike = StringIO.StringIO(filecontent)

            status = '200 OK'
            response_headers = [('Content-Type', ctype), ('Content-Length', str(len(filecontent))), ('Content-Disposition', 'attachment; filename='+filename)]
            start_response(status, response_headers)

            return [filecontent]

           # block_size = 1024
           # if 'wsgi.file_wrapper' in env:
           #     return env['wsgi.file_wrapper'](filelike, block_size)
           # else:
           #     return iter(lambda: filelike.read(block_size), '')

        elif xwd_format == 'xpf':
            ctype = 'application/xml'
            [filecontent, filename] = generate_xpf(xwd_url)
            #filelike = StringIO.StringIO(filecontent)

            status = '200 OK'
            response_headers = [('Content-Type', ctype), ('Content-Length', str(len(filecontent))), ('Content-Disposition', 'attachment; filename='+filename)]
            start_response(status, response_headers)

            return [filecontent]

            #block_size = 1024
            #if 'wsgi.file_wrapper' in env:
            #     return env['wsgi.file_wrapper'](filelike, block_size)
            # else:
            #     return iter(lambda: filelike.read(block_size), '')
        elif xwd_format == 'puz':
            ctype = 'application/octet-stream'
            [filecontent, filename] = generate_puz(xwd_url)
            #filelike = StringIO.StringIO(filecontent)

            status = '200 OK'
            response_headers = [('Content-Type', ctype), ('Content-Length', str(len(filecontent))), ('Content-Disposition', 'attachment; filename='+filename)]
            start_response(status, response_headers)

            return [filecontent]

        else:
            ctype = 'text/plain'
            response_body = 'Error: Unknown output format.'

    else:
        url = 'http://www.hindu.com/crossword'
        parser = etree.HTMLParser()

        try:
            tree = etree.parse(url, parser)
        except IOError:
            response_mid = "<h3>Error: Could not load "+url+"!</h3>";
        else:
            #links_raw = tree.xpath("//a[contains(@href, 'http://www.thehindu.com/crossword/the-hindu-crossword-')]/@href")
            links_raw = tree.xpath("//a[contains(@href, 'http://www.thehindu.com/crossword/the-hindu-crossword-')]")
            
            # link URL pattern
            pattern = 'http://www.thehindu.com/crossword/the-hindu-crossword-(\d{1,})/article(\d{1,}).ece'
            regexp = re.compile(pattern)

            # title pattern
            re0='Published\:\s+'
            re1='((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Sept|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))'	# Month 1
            re2='.*?'	# Non-greedy match on filler
            re3='((?:(?:[0-2]?\\d{1})|(?:[3][01]{1})))(?![\\d])'	# Day 1
            re4='.*?'	# Non-greedy match on filler
            re5='((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'	# Year 1
            title_regexp = re.compile(re0+re1+re2+re3+re4+re5, re.IGNORECASE|re.DOTALL)

            links_match = []
            for link in links_raw:
                if link.get('title'):
                    m = regexp.search(link.get('href'))
                    if m and m.group(0) not in links_match:
                        m_title = title_regexp.search(link.get('title'))
                        if m_title:
                            links_match.append((m.group(1), m.group(0), m_title.group(1)+' '+m_title.group(2)+', '+m_title.group(3)))
                        else:
                            links_match.append((m.group(1), m.group(0), 'Date unknown'))

            #links_match = [x for x in sorted(links_match, reverse=True)]
            
            
            puz_div = etree.Element('div', id='puzzles')
            puz_div.set('class', 'container')
            doc = etree.ElementTree(puz_div)
            #body = etree.SubElement(html, 'body')
            
            xheader = etree.SubElement(puz_div, 'h3')
            xheader.set('class', 'title')
            xheader.text = "Crossword puzzles:"

            # crossword table
            xtable = etree.SubElement(puz_div, 'table', id='xwd-table', cellspacing='0', width='100%')
            xtable.set('class', 'table table-striped table-bordered')
            # table head
            thead = etree.SubElement(xtable, 'thead')
            tr = etree.SubElement(thead, 'tr')
            etree.SubElement(tr, 'th').text = 'Crossword'
            etree.SubElement(tr, 'th').text = 'ipuz'
            etree.SubElement(tr, 'th').text = 'xpf'
            etree.SubElement(tr, 'th').text = 'puz'
            # table body
            tbody = etree.SubElement(xtable, 'tbody')
            for link in links_match:
                tr = etree.SubElement(tbody, 'tr')
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=link[1]).text = "THC "+ link[0] + ": " + link[2]
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link[1],'&format=ipuz'])).text = 'ipuz'
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link[1],'&format=xpf'])).text = 'xpf'
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link[1],'&format=puz'])).text = 'puz'
            
            response_mid = etree.tostring(doc, pretty_print=True, encoding="unicode")

        ctype = 'text/html'
        response_head = '''
<!DOCTYPE html>
<html>
<head>
<!-- CSS Reset -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/3.0.3/normalize.css">
<!-- jQuery -->
<script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-1.12.3.min.js"></script>
<!-- Bootstrap -->
<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
<!-- jQuery dataTables plugin -->
<!-- <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css"> -->
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.12/css/dataTables.bootstrap.min.css">
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.12/js/dataTables.bootstrap.min.js"></script>
<script type="text/javascript">
$(document).ready(function() {
    $('#xwd-table').DataTable( {
        "pagingType": "full_numbers",
        "pageLength": 10,
        "columnDefs": [
        { "orderable": false, "targets": [1, 2, 3] }
        ],
        "order": [ ]
    } );
} );
</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>THCParse</title>
</head>
<body>
<div class="container">

<h2 class="page_title">THCParse</h2>

<div class="info">
This page converts <a href="http://www.thehindu.com/crossword/">
The Hindu Crossword</a> puzzles to the popular open digital crossword formats - 
<a href="http://www.ipuz.org/"><code>ipuz</code></a>(v 1.0) and 
<a href="http://www.xwordinfo.com/XPF/"><code>xpf</code></a>(v 1.0), 
and the <a href="http://www.litsoft.com/">Across Lite <code>puz</code> format.</a></p>

<p>The crossword puzzles, listed in a table below, are fetched from 
<a href="http://www.thehindu.com/crossword/">The Hindu crosswords page</a> every time this page is 
(re)loaded. Therefore, the puzzles listed in this page are up-to-date with the official website.</p>

<p>The files downloaded from this page can be opened with any crossword 
software that supports the corresponding format. Two software which the author recommends are:</p>

<ul>
<li><a href="https://sourceforge.net/projects/wx-xword/">XWord</a> for PC(Linux/Windows), and</li>
<li><a href="https://play.google.com/store/apps/details?id=com.kevinandhari.crosswordsplus&amp;hl=en">Crosswords 
Plus</a> for Mobile(Android) [<i>currently, this software cannot read the <code>ipuz</code> 
files downloaded from this site</i>].</li>
</ul>
</div> <!-- info -->
'''

        response_tail = '''
<hr>

<footer class="footer">
<p>
Created by Jithin Jith on 2016-06-06. 
</p>
</footer>
</div> <!-- container -->
</body>
</html>'''

        response_body = '\n'.join([response_head, str(response_mid), response_tail])
    

    response_body = response_body.encode('utf-8')
    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
    start_response(status, response_headers)

    return [response_body]
#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
    #bjoern.run(application, 'localhost', 8080) # for local testing
