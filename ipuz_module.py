from lxml import etree
import json

#xwd_url = "The Hindu Crossword 11718 - The Hindu.html"
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11718/article8686670.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11717/article8681827.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11716/article8677222.ece'


def generate_ipuz(xwd_url):
    
    parser = etree.HTMLParser()
    try:
        tree = etree.parse(xwd_url, parser)
    except etree.ParseError as e:
        print(e)
    
    date = tree.xpath("//span[@class='dateline']/text()")[1].strip()
    
    title = tree.xpath("//h1[@class='detail-title']/text()")[0]
    
    author = tree.xpath("//span[@class='artauthor']/ul/li/a/text()")

    if author:
        author = author[0]
    else:
        author = ''
    
    xwd_table = tree.xpath("//table[@class='blCrossword cwTable']/tbody")
    if xwd_table == []: # if <tbody> tag is not present 
        xwd_table = tree.xpath("//table[@class='blCrossword cwTable']")
    
    clues_across_raw = tree.xpath("//div[@class='cwClueAcross clueList']/div[@class='clueAcrossList']/ul/li/text()")
    clues_down_raw = tree.xpath("//div[@class='cwClueDown clueList']/div[@class='clueAcrossList']/ul/li/text()")
    across_nums_tree = tree.xpath("//div[@class='cwClueAcross clueList']/div[@class='clueAcrossList']/ul")
    down_nums_tree = tree.xpath("//div[@class='cwClueDown clueList']/div[@class='clueAcrossList']/ul")
    
    clues_across = []
    nums_across = []
    lens_across = []
    
    clues_down = []
    nums_down = []
    lens_down = []
    
    # sanitise across clues
    for clue_raw in clues_across_raw:
        clue = clue_raw.strip()
        if clue == ')': # if clue is just a parenth close, ignore
            pass
        else:
            if clue[-1] == '(': # remove trailing parenth open
                clue = clue[:-1]
            if clue[-1] == ' ': # remove trailing space
                clue = clue[:-1]
    
            clues_across.append(clue)
    
    # sanitise down clues
    for clue_raw in clues_down_raw:
        clue = clue_raw.strip()
        if clue == ')': # if clue is just a parenth close, ignore
            pass
        else:
            if clue[-1] == '(': # remove trailing parenth open
                clue = clue[:-1]
            if clue[-1] == ' ': # remove trailing space
                clue = clue[:-1]
    
            clues_down.append(clue)
    
    for item in across_nums_tree[0]:
        nums_across.append(int(item.get('data-clue-no')))
        lens_across.append(item.xpath("span[@class='clueCount']/text()")[0])
    
    
    for item in down_nums_tree[0]:
        nums_down.append(int(item.get('data-clue-no')))
        lens_down.append(item.xpath("span[@class='clueCount']/text()")[0])
    
    #ipuz_across = [[num, clue] for num, clue in zip(nums_across, clues_across)]
    #ipuz_down = [[num, clue] for num, clue in zip(nums_down, clues_down)]
    ipuz_across = [{'number':num, 'clue':clue, 'enumeration':length} for num, clue, length in zip(nums_across, clues_across, lens_across)]
    ipuz_down = [{'number':num, 'clue':clue, 'enumeration':length} for num, clue, length in zip(nums_down, clues_down, lens_down)]
    
    n_rows = len(xwd_table[0])
    n_cols = len(xwd_table[0][0])
    
    xwd_sol = [None]*n_rows
    xwd_grid = [None]*n_rows
    
    for k, row in enumerate(xwd_table[0]):
        xwd_sol[k] = []
        xwd_grid[k] = []
        for cell in row:
            if cell.get("class") == "blCrossBlock":
                xwd_sol[k].append('#')
                xwd_grid[k].append('#')
            else:
                xwd_sol[k].append(cell.get("data-cw-solution"))
    
                data_cw_number = cell.get("data-cw-number")
                if data_cw_number == None:
                    xwd_grid[k].append(0)
                else:
                    xwd_grid[k].append(int(data_cw_number))
    
    
    ipuz_data = {}
    
    ipuz_data["version"] = "http://ipuz.org/v1"
    ipuz_data["kind"] = ["http://ipuz.org/crossword#1"]
    ipuz_data["dimensions"] = { "width": n_cols, "height": n_rows }
    ipuz_data["showenumerations"] = True
    ipuz_data["title"] = title
    ipuz_data["author"] = author
    ipuz_data["date"] = date
    ipuz_data["puzzle"] = xwd_grid
    ipuz_data["solution"] = xwd_sol
    ipuz_data["clues"] = { "Across": ipuz_across, "Down": ipuz_down }
    
    #ipuz_filename = './test/'+title.replace(' ','_').lower()+'.ipuz'
    #with open(ipuz_filename, 'w') as ipuz_file:
    #    #json.dump(ipuz_data, ipuz_file, indent=0, separators=(',',':'), ensure_ascii=True)
    #    json.dump(ipuz_data, ipuz_file, ensure_ascii=True)
    
    json_string = json.dumps(ipuz_data, ensure_ascii=True)

    filename = title.replace(' ','_').lower()+'.ipuz'

    return [json_string, filename]
