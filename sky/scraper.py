# logging all actions
# simplify
# author! :)
# date removal

import re
import os
import json
import lxml.html
import justext

try:
    from .money import MoneyMatcher
    from .dbpedia import load_dbpedia
    from .dbpedia import get_dbpedia_from_words
    from .language import get_language
    from .images import get_images
except SystemError:
    from money import MoneyMatcher
    from dbpedia import load_dbpedia
    from dbpedia import get_dbpedia_from_words
    from language import get_language
    from images import get_images
    
# dbpedia = load_dbpedia()

money = MoneyMatcher()

try: 
    from .helper import *
    from .templated import DomainNodesDict
    from .findTitle import getRuleTitle
    from .get_date import get_dates
    from .get_author import get_author
    from .links import get_sorted_links
except SystemError: 
    from helper import * 
    from findTitle import getRuleTitle
    from templated import DomainNodesDict
    from get_date import get_dates
    from get_author import get_author
    from links import get_sorted_links

class Scrape():
    # todo is finextr date
    def __init__(self, config): 
        self.config = config
        self.index_required_strings = []
        self.index_filter_strings = []
        self.detected_language = None
        self.seed_urls = None 
        self.domain = None
        self.collections_path  = None
        self.collection_name = None 
        self.template_proportion = None
        self.min_templates = None
        self.max_templates = None 
        self.applyConfigFile() 
        self.domain = extractDomain(self.seed_urls[0])
        self.url_to_tree_mapping  = {}
        self.url_to_headers_mapping = {}
        self.load_pages() 
        self.domain_nodes_dict = DomainNodesDict(self.domain, self.min_templates, self.max_templates, self.template_proportion)
        self.add_template_elements() 

    def should_save(self, url):
        if not self.index_required_strings or any([re.search(condition, url) for condition in self.index_required_strings]):
            if all([not re.search(x, url) for x in self.index_filter_strings]): 
                return True
        return False       
        
    def applyConfigFile(self):
        for config_key, config_value in self.config.items():
            setattr(self, config_key, config_value)
        self.domain = extractDomain(self.seed_urls[0])

    # This will have to be changed into the database variant    
    def load_pages(self): 
        saved_html_dir = os.path.join(self.collections_path, self.collection_name)
        for root, _, files in os.walk(saved_html_dir):
            for name in files:
                if not name.startswith('.DS_'):
                    with open(os.path.join(saved_html_dir, name)) as f:
                        try:
                            js = json.load(f)
                        except UnicodeDecodeError: 
                            print('failed to load json {}'.format(name))
                        try:
                            self.url_to_tree_mapping[js['url']] = makeTree(js['html'], self.domain)
                            self.url_to_headers_mapping[js['url']] = js['headers']
                        except Exception as e:
                            print(str(e))
                        
    def add_template_elements(self): 
        for url in self.url_to_tree_mapping:
            self.domain_nodes_dict.add_template_elements(self.url_to_tree_mapping[url])

    def process(self, url, remove_visuals, exclude_data): 
        tree = self.url_to_tree_mapping[url]
        if self.detected_language is None:
            self.detected_language = get_language(tree, self.url_to_headers_mapping[url], self.domain)
        # print('language: {}'.format(self.detected_language))    
        # pre_text_content = normalize('\n'.join([get_text_and_tail(x) for x in tree.iter()]))

        # author has to be attempted before duplicate removal, since an author is likely to occur more often 
        self.domain_nodes_dict.remove_template(tree)
        hardest_authors, not_hardest_authors, text_hard_authors, text_soft_authors, meta_authors = get_author(tree, self.detected_language)
        self.domain_nodes_dict.remove_author(tree)
        title = getRuleTitle(tree) 
        # filter duplicate images by src
        ok_imgs = get_images(tree)
        titleind = ()
        imginds = []
        contentinds = []

        # such as title, date and later author 

        link_eles = [link[0] for link in tree.iterlinks() if link[0].tag == 'a' and link[2] and link[2].startswith(self.domain)
                     and get_text_and_tail(link[0]).strip()]

        linkinds = []
        for num, node in enumerate(tree.iter()): 
            if node.tag == 'img':
                if node in ok_imgs:
                    imginds.append((node, num))
                node.set('alt', '')
            elif normalize(get_text_and_tail(node)) == title:
                titleind = (node, num)
            elif get_text_and_tail(node).strip():
                if node in link_eles:
                    linkinds.append((node, num))
                contentinds.append((node, num))
            # Cleanup trash for visual'
            if remove_visuals:
                if node.tag == 'input':
                    node.set('type', 'hidden')
                elif node.tag == 'a' and not get_text_and_tail(node).strip():
                    for att in node.attrib:
                        node.set(att, '')
                if node.attrib and 'background-image' in node.attrib:
                    node.set('background-image', '')
        if not titleind: 
            # fuzzy token text / title matching
            title_set = set(title.split())
            for num, node in enumerate(tree.iter()): 
                text_content = get_text_and_tail(node)
                if text_content and len(text_content) < 500: 
                    text_set = set(text_content.split())
                    if fscore(title_set, text_set) > 0.5:
                        titleind = (node, num)
                        break
                    
        if titleind:
            sortedimgs = sorted(imginds, key = lambda x: abs(x[1] - titleind[1]))
        else: 
            sortedimgs = []
        hardest_dates, fuzzy_hardest_dates, not_hardest_dates, soft_dates, non_fuzzy_anys, fuzzy_anys = get_dates(tree, self.detected_language)
        images = []
        for x in sortedimgs:
            src = x[0].attrib['src']
            if src not in images:
                images.append(src)
        
        date = ''
        date_node_index = None
        author = ''
        author_node_index = None
        if titleind:
            # excluding soft dates (meta, they wont work anyway)
            for dt in [hardest_dates, fuzzy_hardest_dates, not_hardest_dates, non_fuzzy_anys, fuzzy_anys]:
                if dt:
                    date, date_node_index = sorted(dt, key = lambda x: abs(x[1] - titleind[1]))[0]
                    break
            for at in [hardest_authors, not_hardest_authors, text_hard_authors, text_soft_authors]: 
                if at:
                    author, author_node_index = sorted(at, key = lambda x: abs(x[1] - titleind[1]))[0]
                    break 
        if not date and soft_dates:    
            for sd in soft_dates:
                date = sd
                break 

        if not author and meta_authors:    
            for ma in meta_authors:
                author = ma
                break     

        if date_node_index is not None: 
            for num, node in enumerate(tree.iter()):
                if num == date_node_index:
                    break 
            # It goes wrong when some year is mentioned in the title, then it removes title    
            # print('removing date content', node.text)
            node.text = ''
            node.tail = ''

        if author_node_index is not None: 
            for num, node in enumerate(tree.iter()):
                if num == author_node_index:
                    break 
            # It goes wrong when some year is mentioned in the title, then it removes title    
            # print('removing author content', node.text)
            node.text = ''
            node.tail = ''

        cleaned_html = lxml.html.tostring(tree).decode('utf8')
        
        body_content = self.get_content(cleaned_html)        

        if not body_content:
            body_content = []
            title_len = len(title)
            title_tokens = set(title.split()) 
            len_title_tokens = len(title_tokens)
            last_text_node_num = get_last_text_non_a_node(tree) 
            for num, x in enumerate(tree.iter()):
                txt = normalize(get_text_and_tail(x))
                if txt:
                    if num < titleind[1]:
                        # print('removed pre-title', txt)
                        x.text = ''
                        x.tail = ''
                        continue
                    if last_text_node_num > 0 and num > last_text_node_num:
                        # print('removed post-content', txt)
                        x.text = ''
                        continue
                    n = len(txt)
                    # remove title
                    txt_tokens = set(txt.split()) 
                    n_matching = len(txt_tokens & title_tokens)
                    if n < title_len * 3 and n_matching / len(txt_tokens) > 0.3 and n_matching / len_title_tokens > 0.3:
                        # print('removed!', txt)
                        continue
                    body_content.append(txt) 

        links = [x.attrib['href'] for x in tree.xpath('//a') if 'href' in x.attrib and x.attrib['href'].startswith(self.domain) and self.should_save(x.attrib['href'])]

        money_amounts = money.find('\n'.join(body_content), 1000) + money.find(title, 1000)

        data = {'title' : title, 
                'body' : body_content, 
                'images' : images, 
                'publish_date' : str(date), 
                'author' : author,
                'cleaned' : cleaned_html, 
                'url' : url, 
                'domain' : self.domain,
                'money': money_amounts,
                'related' : get_sorted_links(links, url)[:5] }

        filtered_data = {k : v for k, v in data.items() if k not in exclude_data}
        
        return filtered_data

    def process_all(self, remove_visuals = False, exclude_data = None, maxn = 100000000):
        if exclude_data is None:
            exclude_data = []
        results = {} 
        for num, url in enumerate(self.url_to_tree_mapping):
            if num > maxn:
                break
            results[url] = self.process(url, remove_visuals, exclude_data)
        return results

    def get_content(self, html):
        lang_mapping = {'nl' : 'Dutch', 'en' : 'English', 'com' : 'English'}
        if self.detected_language not in lang_mapping:
            return ''
        lang = lang_mapping[self.detected_language]
        body_content = [x.text for x in justext.justext(html, justext.get_stoplist(lang)) 
                        if not x.is_boilerplate and not x.is_heading]
        return body_content

# from configs import DEFAULT_CRAWL_CONFIG
# from helper import *

# SCRAPE_CONFIG = DEFAULT_CRAWL_CONFIG.copy()

# SCRAPE_CONFIG.update({ 
#     'collections_path' : '/Users/pascal/GDrive/siteview/collections/',
#     'seed_urls' : ['http://www.nu.nl'],
#     'collection_name' : 'nu.nl',
#     'template_proportion' : 0.09,
#     'max_templates' : 1000
# })

# ind = Scrape(SCRAPE_CONFIG)

# r = ind.process_all()







