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
            links_raw = tree.xpath("//a[contains(@href, 'http://www.thehindu.com/crossword/the-hindu-crossword-')]/@href")
            
            pattern = 'http://www.thehindu.com/crossword/the-hindu-crossword-(\d{1,})/article(\d{1,}).ece'
            regexp = re.compile(pattern)
            
            links_match = [m.group(0) for x in links_raw for m in [regexp.search(x)] if m]
            
            links = [x for n,x in enumerate(links_match) if x not in links_match[:n]]
            links_text = [' '.join(['THC', m.group(1)]) for x in links for m in [regexp.search(x)] if m]
            
            puz_div = etree.Element('section', id='puzzles')
            puz_div.set('class', 'container')
            doc = etree.ElementTree(puz_div)
            #body = etree.SubElement(html, 'body')
            
            #etree.SubElement(body, 'h1').text = "Convert The Hindu Crossword to 'ipuz' and 'xpf' formats"
            #etree.SubElement(body, 'p').text = "Download the ipuz/xpf files and solve the crossword on your PC/mobile."
            #etree.SubElement(body, 'h3').text = "Software:"
            #sw_list = etree.SubElement(body, 'ul')
            #sw_pc = etree.SubElement(sw_list, 'li')
            #sw_pc.text = "PC(Linux/Windows):    "
            #etree.SubElement(sw_pc, 'a', href="https://sourceforge.net/projects/wx-xword/").text = "XWord"
            #sw_mob = etree.SubElement(sw_list, 'li')
            #sw_mob.text = "Mobile(Android):    "
            #etree.SubElement(sw_mob, 'a', href="https://play.google.com/store/apps/details?id=com.kevinandhari.crosswordsplus&hl=en").text = "Crosswords Plus (only reads xpf)"
            
            xheader = etree.SubElement(puz_div, 'h3')
            xheader.set('class', 'title')
            xheader.text = "Crossword puzzles:"
            #ulist = etree.SubElement(puz_div, 'ul')
            xtable = etree.SubElement(puz_div, 'table')
            tbody = etree.SubElement(xtable, 'tbody')
            for link, text in zip(links, links_text):
                #li = etree.SubElement(ulist, 'li')
                #li.text = text
                #etree.SubElement(li, 'span').text = '   '
                #etree.SubElement(li, 'a', href=''.join(['?xwd_url=',link,'&format=ipuz'])).text = 'ipuz'
                #etree.SubElement(li, 'span').text = '   '
                #etree.SubElement(li, 'a', href=''.join(['?xwd_url=',link,'&format=xpf'])).text = 'xpf'
                tr = etree.SubElement(tbody, 'tr')
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=link).text = text
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link,'&format=ipuz'])).text = 'ipuz'
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link,'&format=xpf'])).text = 'xpf'
                td = etree.SubElement(tr, 'td')
                etree.SubElement(td, 'a', href=''.join(['?xwd_url=',link,'&format=puz'])).text = 'puz'
            
            response_mid = etree.tostring(doc, pretty_print=True, encoding="unicode")

        ctype = 'text/html'
        response_head = '''
<!DOCTYPE html>
<html>
<head>
<!-- Google Fonts -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
<!-- CSS Reset -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/3.0.3/normalize.css">
<!-- Milligram CSS minified -->
<link rel="stylesheet" href="static/milligram.min.css">
<title>THCParse</title>
</head>
<body>
<main class="wrapper">
<header class="header">
<section class="container">
<h2 class="title">THCParse</h2>
<p class="description">This page converts <a href="http://www.thehindu.com/crossword/">
The Hindu Crossword</a> puzzles to the popular open digital crossword formats - 
<a href="http://www.ipuz.org/"><code>ipuz</code></a>(v 1.0) and 
<a href="http://www.xwordinfo.com/XPF/"><code>xpf</code></a>(v 1.0), 
and the <a href="http://www.litsoft.com/">Across Lite <code>puz</code></a> format.</p>
</section>
</header>
<section class="container">
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
</section>
'''

        response_tail = '''
<footer class="footer">
<section class="container">
<p>
Created by Jithin Jith on 2016-06-06. 
<!-- Page designed using the <a href="https://milligram.github.io/">Milligram</a> CSS framework.</p> -->
</p>
</section>
</footer>
</main></body></html>'''

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
