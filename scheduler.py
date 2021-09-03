# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:31:57 2021

@author: beccamayers
"""
import schedule
from datetime import datetime
from report_bot import get_report
import time


now = datetime.now()
timestamp = now.strftime("%b%d%Y %H%M%p")

def job():
    print("Launching Report Bot app...")
    get_report()


schedule.every().hour.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)