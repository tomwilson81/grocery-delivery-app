import requests
from datetime import datetime, timedelta
import os
from twilio.rest import Client


url = "https://groceries.asda.com/api/v3/slot/view"

# start_date = datetime.today().date().strftime('%Y-%m-%dT%H:%M:%S')
# end_date = (datetime.today().date() + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S')

json_data = {"requestorigin":"gi",
            "data": {"service_info":{"fulfillment_type":"DELIVERY",
                                    "enable_express":'true',"is_unattended_slot":'false',
                                    "is_flex_slot":'false',"is_eat_n_collect":'false'},
                    "reserved_slot_id":"",
                    "request_window":"P2D",
                    "service_address":{"postcode":"HX28TN","latitude":"53.734792","longitude":"-1.890971"},
                    "customer_info":{"account_id":"44588672-e335-4869-8ec3-93fdb0f7b53f"},
                    "order_info":{"order_id":"e3264000-20ce-11ed-8bd4-bd56b85bedd8","parent_order_id":"","restricted_item_types":[],"sub_total_amount":0}}}

# Make POST request to API, sending required json data
r = requests.post(url, json=json_data)

print(r.status_code)

# print(r.json())

# INITIATE EMPTY DICTIONARY
slot_data = {}

# LOOP THROUGH JSON SLOT DATA AND EXTRACT SLOT AVAILABILITY
for slot_day in r.json()['data']['slot_days']:
    slot_date = slot_day['slot_date']

    for slot in slot_day['slots']:
        slot_time = slot['slot_info']['start_time']
        slot_time = datetime.strptime(slot_time, '%Y-%m-%dT%H:%M:%SZ')

        slot_status = slot['slot_info']['status']
        
        slot_data[slot_time.strftime('%H:%M:%S %d-%m-%Y')] = slot_status

print(slot_data)

# Filter for available slots
available_slots_list = [f"/n {key} - {value}" for (key,value) in slot_data.items() if value!='UNAVAILABLE']

# If any available slots exist, send a text notification
if len(available_slots_list) > 0:

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message_txt = f'\n Delivery Slot/s Found: \n{" ".join(available_slots_list)}'

    # print(message_txt)

    message = client.messages \
                .create(
                     body = message_txt,
                     from_= os.environ['TWILIO_NUMBER'],
                     to = os.environ['MY_NUMBER']
                 )

