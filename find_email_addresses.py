'''
Created on Oct 20, 2015

@author: Priyanka
'''
from bs4 import BeautifulSoup
from selenium import webdriver
from sets import Set
import sys
import datetime
import tldextract
import re

email_list=Set([]) 

def main():
    try:
        if len(sys.argv) == 3:
            domain_name = sys.argv[1]
            max_depth = sys.argv[2]
            
        elif len(sys.argv) == 2:
            domain_name = sys.argv[1]
            max_depth = 2 #setting default maximum depth
        else:
            print("USAGE --> python find_email_addresses.py <<domain_name>> [maximum_depth]")
            sys.exit(-1)
        crawl(domain_name, max_depth)
    except Exception:
        raise


#Using BeautifulSoup to extract page content
def extract_soup(driver, current_link):
    #Loading the Selenium driver with the current link
    driver.get(current_link)  
    beautiful_soup = BeautifulSoup(driver.page_source, "html.parser")
    return beautiful_soup


# This method uses the information from crawl and looks up the href attribute value for necessary information
def lookup_href_attribute(child_urls, visited_links, email_list, href_attribute, domain):
    mailTag="mailto"
    if href_attribute:
        #Extracting top level domain information from the given domain
        given_domain_ext = tldextract.extract(domain)
        #Extracting top level domain information from the current link
        href_ext = tldextract.extract(href_attribute)
        #Matching the domain name in the links and emailIDs found on the webpage
        domain_found = (str(given_domain_ext.domain) == str(href_ext.domain)) and (str(given_domain_ext.suffix) == str(href_ext.suffix))
        if domain_found:  
            # Extracting emails 
            if mailTag in str(href_attribute):
                mail = href_attribute.split(":")
                #Regex for email
                match = re.search(r'(\w+[.|\w])*@(\w+[.])*\w+', mail[1])
                if match:
                email_list.add(match.group())
            # Checking if the link is valid 
            elif check_valid_link(href_attribute, visited_links, child_urls):
                child_urls.add(href_attribute)

# This method takes the given domain and maximum depth and performs a web crawl
def crawl(domain_name, max_depth):
    
    child_urls = Set([]) 
    seed_url = "http://{}/".format(domain_name)
    links_to_crawl = Set([seed_url])
    visited_links = Set([])
    current_depth = 1
    
    driver = webdriver.Firefox()
    try:
        # do while there are enough links to crawl and maximum depth is not reached
        while len(links_to_crawl)!=0 and current_depth<= int(max_depth):
            current_link = links_to_crawl.pop()
            if check_valid_link(current_link, visited_links):
                content = extract_soup(driver, current_link)
                # Skipping links with rel as canonical
                for link in content.findAll('link', rel="canonical"):
                    visited_links.add(link["href"])
                # Fetching all anchor tags
                anchor_tags = content.find_all('a')
                for tag in anchor_tags:
                    # Fetching href attribute value for every anchor tag
                    href_attribute = tag.get('href')
                    lookup_href_attribute(child_urls, \
                                             visited_links, email_list, \
                                             href_attribute, domain_name)
                visited_links.add(current_link)
                
            if len(links_to_crawl) == 0:
                links_to_crawl = child_urls
                # Incrementing depth
                current_depth = current_depth + 1 
                child_urls = Set([])
                
    except Exception:
        write_output(email_list);
        
    driver.close()
    write_output(email_list)
    
#This method checks if the given URL can be crawled or not    
def check_valid_link(link,urls1,urls2=None):
    
    if urls2 is None:
        return link not in urls1
    else:
        return link not in urls1 and link not in urls2



def write_output(email_list):
    try:
        #Writing all emails collected to a file called emails.txt
        output_file = open("emails.txt", "w")
        for email in email_list:
            output_file.write(str(email)+'\n')
    except IOError:
        print "Exception: Can't write to Emails.txt"
        
        
if __name__ == '__main__':
    main()