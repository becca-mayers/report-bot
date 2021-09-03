# report-bot
Beautiful summary report on autopilot.

Looking to healthcare for this report bot, it generates (data_generator.py) and calculates (report_variables.py) randomized monthly (https://www.ahrq.gov/ncepcr/care/coordination/mgmt.html)[care management] metrics (Length of Stay, Inpatient Cases Exceeding 48 Hours, etc.) for July 2019 to present along a fictitious facility set named after the (https://en.wikipedia.org/wiki/NATO_phonetic_alphabet)[military alphabet]. (Note: metrics from any industry are fodder for a report bot.)

It then ranks (report_bot.py) each metric from lowest to highest (where lower is better) and from highest to lowest (where higher is worse), indicating the three lowest facilities as top performers and the three highest facilities as bottom performers for the current month.

Next, it finds the percentage change from the previous month as compared to the current month for each metric and ranks the military alphabet facilities again based on the three greatest decreases ("Best Progress") and the three greatest increases ("Worst Progress") for the current month.

From there, it creates a randomized set of recommendations, intended as a placeholder for true recommendations derived from the report's findings. 

All of this is then pushed via jinja to an HTML template inspired by (https://demos.creative-tim.com/material-dashboard/examples/dashboard.html)[Creative Tim's Material Dashboard] Bootstrap components and elements and automated via a scheduler (scheduled.py).

# Result
![short-report](https://user-images.githubusercontent.com/90014766/131937347-d7834cd2-fc10-4c55-aa53-1f0d015678a4.png)

Questions? Find out more (https://www.beccamayers.com)[here].
