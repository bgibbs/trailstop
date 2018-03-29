Trailing Stop Monitoring Script
--------------------------------


Use this to cut your losers short and to let your winners run. Portfolio
gain/loss doesn't matter only whether position is right or wrong.  This
application will give you a summary ordered from wrong to right.

The script evaluates all of your stops and sends an email update. Run it from
crontab once per day after closing.


------------------------------------------------------------------------
Instructions:

1. Create folio.csv.

   Option 1:
   In a text editor enter "symbol,high,low,stop" as the first line.
   Enter your portfolio below this.

   Option 2:
   Download your portfolio from yahoo as quotes.csv or create a csv file
   with format symbol,price.

   Run the script with --start quotes.csv to generate the initial folio.csv

2. Add high, low, and stop to folio.csv

   a. High is the highest closing price for the security since you entered the
      trade. This is entered once by hand, then updated automatically every day.
      If you just entered the trade today, then use your entry price.

   b. Low is the lowest closing price for the security since you entered the
      trade. This is entered once by hand, then updated automatically every day.
      If you just entered the trade today, then use your entry price.

   c. Stop takes the following format:

      1. Trailing for short position: NN.N%
      2. Trailing for long position: -NN.N%
      3. Hard stop for short position: NN.NN
      4. Hard stop for long position: -NN.NN

3. Test from the command line.

   > python trailstop.py

   You should see the daily update.

4. Enter it into crontab (Linux instructions)

   ```
   crontab -e

   0 17 * * 1-5    cd /home/<homedir>/Projects/trailstop; ./trailstop.py \
                      -a <name>@gmail.com -p <password> 
   ```

   This example runs every day at 5 PM and send the report to `<name>@gmail.com`

5. If you don't use gmail, then figure out the smtp address for your mail
   server and pass it with the --smtp option.

6. Some notes about getting reliable closing prices.  The Yahoo Finance API 
   no longer seems to work after many years of reliable use.  The Google API
   is unreliable often failing to return a quote or multiple quotes.
   I have added a TD Ameritrade API.  This requires the user to create
   a developer account at TD Ameritrade and register an application.
   It is not necessary to be a TD Ameritrade customer.
