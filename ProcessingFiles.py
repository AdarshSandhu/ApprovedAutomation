import os
import pandas as pd
import re
import requests
import datetime


checkLineRegex = "lines\-(.*?)\n"
reassessedDateRegex = "ReassessedDate\-(.*?)\n"
sinRegex = "SIN\-(.*?)\n"
oppidRegex = "OppId\-(.*?)\n"
statementLineRegex = "(.*?)\t(.*?)\t(.*?)\t(.*?)\t([\w\,\-\d\.]*)"
#text_file = open("C:\\Users\\Ben\\OneDrive\\Desktop\\Temp\\Statements.txt", "r")
#data = text_file.read()
#text_file.close()
#statementDF = pd.DataFrame(re.findall(statementLineRegex,data),columns=['Date','Details','Amount Debited','Amount Credited','Balance'])
#statementDF.drop(statementDF[statementDF['Date']=='Date'].index,inplace=True)
#statementDF.reset_index(inplace = True, drop = True)

companyRevenue = 0.0
netRefund = 0.0
debtOnClient = 0.0
first = 0
SIN = ""
oppId = ""
reassessedDate = ""
availableFlag = 0


def compute(fileName,year):
    global companyRevenue
    global netRefund
    global debtOnClient
    global first
    global checkLineRegex
    global SIN
    global oppId
    global reassessedDate
    global availableFlag
    availableFlag = 0
    lineRegex = "([\d\-]+)\t(.*?)\t([\d\.\,\-]+)\t([\d\.\,\$\-]+)"
    text_file = open("C:\\Users\\Ben\\OneDrive\\Desktop\\Temp\\"+fileName, "r")
    data = text_file.read()
    text_file.close()

    reassessedDate = re.findall(reassessedDateRegex,data,re.I)[0]
    SIN = re.findall(sinRegex,data,re.I)[0]
    oppId = re.findall(oppidRegex,data,re.I)[0]

    
    checkLines = re.findall(checkLineRegex,data,re.I)[0].split(',')
    lineDF = pd.DataFrame(re.findall(lineRegex,data,re.I),columns=['Line No','Description','Previous Amount','Revised Amount'])

    for i in lineDF['Line No']:
        for j in checkLines:
            if i==j:
                availableFlag = 1
                break

    if availableFlag == 0:
        return
    
    #print(lineDF[['Description','Line No']])
    #print(lineDF[lineDF['Description']=='Balance from this (re)assessment']['Revised Amount'].values[0])
    companyRevenue = companyRevenue + float(lineDF[lineDF['Description']=='Balance from this (re)assessment']['Revised Amount'].values[0].replace('$','').replace(',',''))
    temp = lineDF[lineDF['Description']=='Previous account balance']['Revised Amount'].values
    if len(temp) > 0 and first == 0:
        debtOnClient = float(temp[0].replace('$','').replace(',',''))
    first=1
    #print(lineDF[lineDF['Description']=='Final balance']['Revised Amount'].values[0])
    netRefund = netRefund + float(lineDF[lineDF['Description']=='Final balance']['Revised Amount'].values[0].replace('$','').replace(',',''))
    

files = os.listdir(r"C:\Users\Ben\OneDrive\Desktop\Temp")
for i in files:
    if len(i)<11 and i.endswith('txt'):
        compute(i,i[:-4])

print("Net Refund:- "+str(netRefund))
totalRefund = companyRevenue
print("Total Refund:- "+str(totalRefund))
companyRevenue = round(companyRevenue/100*-33)
print("Company Revenue:- "+str(companyRevenue))
print("Debt on Client:- "+str(debtOnClient))
netAmount = abs(totalRefund) - debtOnClient
if netAmount < 0:
    netAmount = 0
print("Net Amount:- "+str(netAmount))
print(reassessedDate)

reassessedDate = datetime.datetime.strptime(reassessedDate,'%d %b %Y').strftime('%Y-%m-%d')
print(datetime.datetime.now().strftime('%Y-%m-%d'))

url = "https://www.ftrcrm.com/tprest/v1/saveapproveddata" 
headers = {"auth-token": "ab0b618d4613bf6ddb9f9c49bfd9f1a2"}
data = {
  "opp_id": oppId,
  "sin": SIN,
  "record_date": datetime.datetime.now().strftime('%Y-%m-%d'),
  "total_refund": str(totalRefund),
  "owes_to_cra": str(debtOnClient),
  "date_processed": reassessedDate,
  "owes_other_agencies": "0",
  "type_rrsp": "0",
  "company_revenue": str(companyRevenue),
  "estimated_net_refund": str(netAmount),
  "type_northern_resident_deduction": "0",
  "type_disability": "0",
  "type_caregiver": "0",
  "type_non_cap_loss": "0",
  "type_net_capital_loss": "0",
  "type_eligible_dependent": "0",
  "type_hba": "0",
  "type_spousal": "0",
  "type_witb": "0",
  "type_caregiver_dependant": "0",
  "type_child_amount_until_2014": "0",
  "type_tuition": "0",
  "type_medical_expense": "0",
  "files": {
    "noa": "Not Available"
  }
}

if availableFlag == 1:
    requests.post(url, headers=headers, json=data)
    file1 = open(r"C:\Users\Ben\OneDrive\Desktop\Approved-Automation\Logs.txt", "a")  # append mode
    file1.write(str(data))
    file1.close()
