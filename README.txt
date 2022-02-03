Code to scrape punting play-by-play data from pro-football-reference.com
and calculate Jon Boi's Surrender Index.

Requires:
  pandas
  html5lib
  beautifulsoup4
  lxml

Files:
    main.py: Our main loop- calculates the numbers we need for our Bayesian posterior.
             Scrapes every game for 10 years, so takes ~30 minutes or so
    scraping_functions.py: Functions to scrape play-by-play, punts, weekly schedules, and game links
    parsing_functions.py: Functions to convert scraped tables into something useful
    scoring_functions.py: Functions to calculate the Surrender Index and it's intermediate values

To reproduce:
    Simply run main.py, results will be printed
