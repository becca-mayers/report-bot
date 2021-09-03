# report-bot
Beautiful summary report on autopilot.

This report bot generates and calculates randomized monthly [care management](https://www.ahrq.gov/ncepcr/care/coordination/mgmt.html) metrics for July 2019 to present along a fictitious facility set named after the [military alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet). Metrics from any industry are fodder for a report bot.

It then ranks the metrics from lowest to highest (where lower is better) and from highest to lowest (where higher is worse), indicating the three lowest facilities as top performers and the three highest facilities as bottom performers for the current month. Next, it finds the percentage change from the previous month as compared to the current month for each metric and ranks the military alphabet facilities again based on the three greatest decreases and the three greatest increases (Best/Worst Progress) for the current month. From there, it creates a randomized set of recommendations, intended as a placeholder for true recommendations derived from the report's findings. 

All of this is then pushed via jinja to an HTML template inspired by [Creative Tim's Material Dashboard](https://demos.creative-tim.com/material-dashboard/examples/dashboard.html) Bootstrap components and elements and automated via a scheduler.

# Result 
![short-report](https://user-images.githubusercontent.com/90014766/131937347-d7834cd2-fc10-4c55-aa53-1f0d015678a4.png)
Note: Example report truncated to a single metric for space purposes.

# To Run
Following the download and unzip, update the scheduler's frequency if needed (codebase set to run hourly), and launch the scheduler from the command line by cd'ing into the unzipped folder and running the command  `python scheduler.py`.

# Head's Up
You'll need to [install](https://wkhtmltopdf.org/downloads.html) and setup [wkhtmltopdf](https://github.com/wkhtmltopdf/wkhtmltopdf) for HTML to PDF conversion if you haven't already.

Questions? Find out more [here](https://www.beccamayers.com).
