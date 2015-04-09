#Pretraga izvestaja o troskovima kampanje
# -*- coding: utf-8 -*-
import requests
import re

from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup
from slugify import slugify
from bson import json_util

import mechanize

# Connect to defualt local instance of MongoClient
client = MongoClient()

# Get database and collection
db = client.arcas_troskovi_kampanje

def scrape():

    db.assetsandincomes.remove({})

    br = mechanize.Browser()
    br.set_handle_robots(False)   # ignore robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.addheaders = [('User-agent', 'Firefox')]

    search_post_req_url = "http://www.acas.rs/acasPublic/pretragaTroskoviKampanje.htm"
    search_post_req_payload = {
        'sEcho':3,
		'iColumns':6,
		'sColumns': '',
		'iDisplayStart':0,
		'iDisplayLength':10,
		'mDataProp_0':0,
		'mDataProp_1':1,
		'mDataProp_2':2,
		'mDataProp_3':3,
		'mDataProp_4':4,
		'mDataProp_5':5,
		'politickiSubjektId':'',
		'izborNaziv':'',
		'nivoIzboraId':'',
		'vrstaIzboraId':'',
    	}
    r = requests.post(search_post_req_url, data=search_post_req_payload)
    json_resp = r.json()

    data_list = json_resp['aaData']


    for data in data_list:
    	
        naziv_izbora = data[0]
        #print naziv_izbora
        datum_odrzavanja_izbora = data[1]
        #print datum_odrzavanja_izbora
        politicki_subjekti = data[2]
        #print politicki_subjekti
        mesto_podnosenja = data[3]
        #print mesto_podnosenja
        datum_podnosenja = data[4]
        #print datum_podnosenja
        func = data[5]
        

        func = data[5] \
            .replace('<span onmouseover="textUnderline(this);" onmouseout="textNormal(this);" >', '') \
            .replace('</span>', '') \
            .strip() \
            .split('<br>')
        

        # Get the report IDs for the result row, can be multiple
        regex = re.compile(r"\(\d+\)")
        matches = regex.findall(data[5])
        

        # For each report ID, fetch the page.
        for match in matches:
            report_id = match. \
                replace('(', ''). \
                replace(')', '')
        

            details_get_req_url = "http://www.acas.rs/acasPublic/izvestajKampanjeForm.htm?izvestajId=%s" % report_id

            report_page = br.open(details_get_req_url)

            report_page_html_str = report_page.read()
            report_page_soup = BeautifulSoup(report_page_html_str)
            

            #Politicki subjekti
            data_tables = report_page_soup.findAll('table')
            assets_and_incomes_table = data_tables[4]
            assets_and_incomes_table_rows = assets_and_incomes_table.findAll('tr')

            # print assets_and_incomes_table
            # assets_and_incomes_table_rows = data_tables.findAll('tr')
            #Ovlasceno lice
            #table_list = json_resp['aaData']
            #print table_list
            #print assets_and_incomes_table
            #for data in table_list

            #prop_names = []

            for row_index, row in enumerate(assets_and_incomes_table_rows):

                doc = {
                	'naziv_izbora': naziv_izbora,
                	'datum_odrzavanja_izbora': datum_odrzavanja_izbora,
                	'politicki_subjekti': politicki_subjekti,
                	'mesto_podnosenja': mesto_podnosenja,
                	'datum_podnosenja': datum_podnosenja,
                	'func': func,
                	'izvestajID': int(report_id),
                	'properties': [], 
                }
               	header_cells = row.findAll('td')
               	index = header_cells[0].text
               	for i in index:
               		value = row.findAll('input')
               	print index, value





               	
               		# doc['properties'].append({
                 #            'property': index,
                 #            'value': value
                 #        })
               	
                # Get property names from table header
                # if row_index == 0:
                #     header_cells = row.findAll('td')
                #     for header_cell in header_cells:
                #         prop_names.append(header_cell.text)
                
                # # Get property values for each row
                # else:
                #     for column_index, cell in enumerate(row.findAll('td')):
                        
                #         prop_name = prop_names[column_index]
                #         print '%s: %s' % (prop_name, cell.text)

                #         # Create subdoc for the report doc
                #         doc['properties'].append({
                #             'property': prop_name,
                #             'value': cell.text
                #         })


                    
                    # Save doc in database.
                    # WARNING: We don't create a doc with the entire table date on it.
                    # We create one doc per table row.
                    # Can change this structure if we want.
                #db.assetsandincomes.insert(doc)
                    

            # In the future, will have to consider the number of data tables
            '''
            if len(data_tables) == 8:

            elif len(data_tables) == 9:

            else:
                print 'Invalid number of data tables'
            '''

# Let's scrape.
scrape()