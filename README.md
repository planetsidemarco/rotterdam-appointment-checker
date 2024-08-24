# Rotterdam Municipality Appointment Checker

Small codebase to help me scrape the https://www.rotterdam.nl/eerste-inschrijving-in-nederland/start-eerste-inschrijving-in-nederland website for available appointment dates and times.

## Script

Uses Selenium to scrape and explore a webform from the above URL to find the next available appointment date and times for the Rotterdam municipality.

Outputs a text file of next earliest appointment time, screenshot of that option, and screenshot of calendar availability.

## Docker

Building docker container with command: ```docker build --no-cache -t rotterdam .```

Running interactive docker container with command: ```docker run -it --rm -v $(pwd):/usr/src/app -e DISPLAY=:99 rotterdam```

## Cronjob

Running cronjob every 6 hours with command (`crontab -e`):

`0 */6 * * * cd /home/ec2-user/rotterdam-appointment-checker/ && docker run --rm -v $(pwd):/usr/src/app rotterdam >> /home/ec2-user/logfile.log 2>&1`
