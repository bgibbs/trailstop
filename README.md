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

   a. High is the highest closing price for the security since you entered the        trade.

   b. Low is the lowest closing price for the security since you entered the
      trade.

   c. Stop takes the following format:

      1. Trailing for short position: NN.N%
      2. Trailing for long position: -NN.N%
      3. Hard stop for short position: NN.NN
      4. Hard stop for long position: -NN.NN

3. Test from the command line.

   > python trailstop.py

   You should see the daily update.

4. Enter it into crontab (Linux instructions)

   > crontab -e

   > 0 17 * * 1-5    cd /home/<name>/Projects/trailstop; ./trailstop.py \
   >                   -a <nnn>@gmail.com -p <password> 

   This example runs every day at 5 PM and send the report to <nnn>@gmail.com

5. If you don't use gmail, then figure out the smtp address for your mail
   server and pass it with the --smtp option.
