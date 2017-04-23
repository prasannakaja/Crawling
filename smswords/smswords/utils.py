from datetime import datetime
import MySQLdb
import json

from scrapy.conf import settings


def createDBConnection():
    conn = MySQLdb.connect(host=settings['HOST'], user=settings["USER"],\
            passwd=settings["PASSWD"], db=settings["DATABASE"], charset="utf8", use_unicode=True)

    cursor = conn.cursor()

    return conn, cursor

def update_crawl_status(aux_info):
    conn, cursor = createDBConnection()
    aux = {"HttpStatus": aux_info["status"]}

    query = "INSERT INTO advert_crawl_status(url, proxy_info, status, auxilary_info, \
                created_at, updated_at) values (%s, %s, %s, %s, %s, %s)"
    values = (aux_info["url"], aux_info["proxy"], aux_info["crawl_status"], \
                str(aux), current_timestamp(), current_timestamp())
    cursor.execute(query, values)
    conn.commit()

    ## Close DB connection
    cursor.close()
    conn.close()

def current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def getLocationID(location, loc_type=""):
    """
    :type loc_type: string value.(city/area/district)
    """
    conn, cursor = createDBConnection()
    area_id = city_id = 0

    if loc_type == "city":
        query = "SELECT id FROM cities WHERE name='%s' and country_code='ES'"
        cursor.execute(query %location)
        print cursor.fetchall()
        city_id = cursor.fetchall()[0][0] if cursor.fetchall() else 0
    else:
        query = "SELECT id, city_id FROM areas WHERE name='%s' and city_id  \
            in (SELECT id FROM cities WHERE country_code='ES')"
        cursor.execute(query %location)

        for row in cursor.fetchall():
            area_id = row[0]
            city_id = row[1]

    cursor.close()
    conn.close()

    return area_id, city_id

def make_proxy_list(proxy_ids):
    conn, cursor = createDBConnection()
    
    final_proxy_list = []
    for pid in proxy_ids:
        cursor.execute("SELECT  ip,username,password,port,id FROM proxies WHERE ID ='%s'" %pid)
        for row in cursor.fetchall() :
            ip = row[0]
            username = row[1]
            password = row[2]
            port= row[3]
            if username != '':
                fpx = "%s:%s@%s:%s" %(str(username), str(password), str(ip), str(port))
            else:
                fpx = "%s:%s" %(str(ip), str(port))

            final_proxy_list.append(fpx)

    cursor.close()
    conn.close()

    return final_proxy_list

def get_country_details():
    conn, cursor = createDBConnection()

    domain_name = settings["DOMAIN"].split('www.')[-1].strip()
    cursor.execute("select proxy_countries,id,max_proxies from classified_websites where domain = '%s' " %domain_name)
   
    for result in cursor.fetchall():
        ccode_data =json.loads(result[0])
        country_id = result[1]
        max_proxies = result[2]

    cursor.close()
    conn.close()

    return ccode_data, country_id, max_proxies

def getProxies():
    conn, cursor = createDBConnection()

    ## Country Details
    country_code_data, country_id, max_proxies = get_country_details()

    new_proxy_ids = []
    for ccode in  country_code_data:
        cursor.execute("SELECT id FROM proxies WHERE COUNTRY_CODE ='%s' AND ID NOT IN \
            (SELECT PROXY_ID FROM classified_websites_proxies WHERE classified_id='%s')" %(ccode, country_id))
        
        for pd in cursor.fetchall():
            new_proxy_ids.append(pd[0])

    if new_proxy_ids:
        for pd in new_proxy_ids:
            cursor.execute("INSERT INTO classified_websites_proxies (classified_id, proxy_id, status, \
                suspended_level,created_at,updated_at) VALUES (%s,%s,%s,%s,%s,%s)", \
                    (country_id, pd, "online", "0", current_timestamp(), current_timestamp()) )
            conn.commit()

    
    current_proxy_list = []

    cursor.execute("SELECT proxy_id FROM classified_websites_proxies WHERE classified_id='%s' AND (STATUS='online' or \
           (status='suspended' and updated_at < NOW() - INTERVAL 1 HOUR and suspended_level = '1')\
        or (status='suspended' and updated_at < NOW() - INTERVAL 3 HOUR and suspended_level = '2') \
        or (status='suspended' and updated_at < NOW() - INTERVAL 6 HOUR and suspended_level = '3') \
        or (status='suspended' and updated_at < NOW() - INTERVAL 12 HOUR and suspended_level = '4') \
        or (status='suspended' and updated_at < NOW() - INTERVAL 24 HOUR and suspended_level = '5') \
        or (status='suspended' and updated_at < NOW() - INTERVAL 30 HOUR and suspended_level = '6')) " %country_id)

    for row in cursor.fetchall():
        current_proxy_list.append(row[0])
    
    cursor.close()
    conn.close()

    prepared_proxy_list = make_proxy_list(current_proxy_list)

    return prepared_proxy_list[:max_proxies]
        
    
def proxySuspended(proxy_suspended):
    proxy_ip = proxy_suspended.split('@')[-1].split(':')[0]
    port =  proxy_suspended.split(':')[-1]

    country_code_data, country_id, max_proxies = get_country_details()
    
    suspended_level = 0

    conn, cursor = createDBConnection()

    ## GET PROXY ID
    cursor.execute("SELECT id FROM proxies WHERE ip ='%s' AND port ='%s'" %(proxy_ip, port))
    proxy_id = cursor.fetchall()[0][0] if cursor.fetchall() else ""

    ## GET SUSPENDED LEVEL
    cursor.execute("SELECT suspended_level FROM classified_websites_proxies WHERE proxy_id ='%s' \
            and classified_id='%s'" %(proxy_id, country_id))

    suspended_level = int(cursor.fetchall()[0][0]) if cursor.fetchall() else 0
    suspended_level += 1

    cursor.execute("UPDATE classified_websites_proxies SET updated_at='%s', status='suspended', \
                         suspended_level='%s' WHERE proxy_id ='%s' and classified_id='%s'" \
                            %(current_timestamp(), suspended_level, proxy_id, country_id))
    conn.commit()

    cursor.close()
    conn.close()
    
def insertPhoneNumber(city, area, district, phone_number):
    city_name = city.lower().replace('-','_').replace(' ','_')
    area_name = area.lower().replace('-','_').replace(' ','_')
    district_name = district.lower().replace('-','_').replace(' ','_')
    
    conn, cursor = createDBConnection()

    cursor.execute("SELECT id, city_id FROM areas WHERE name='%s' and city_id  in \
            (select id from cities where country_code = 'ES') " %(area_name))

    for row in cursor.fetchall():
        pn_area_id = row[0]
        pn_city_id = row[1]

    pn_district_id = 0


    cursor.execute("INSERT INTO mobile_numbers (`number`, `country_code`, postal_code_id, created_at, \
            updated_at, city_id, area_id, district_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (str(phone_number), \
                str(country_code), "0", current_timestamp(), current_timestamp(), str(pn_city_id), \
                    str(pn_area_id), str(pn_district_id)))
    conn.commit()

    cursor.close()
    conn.close()






