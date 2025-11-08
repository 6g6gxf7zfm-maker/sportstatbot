# 🚀 Quick Start Guide

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Configure API keys
cp .env.example .env
# Edit .env if you have API keys
```

## Try the Demo

See what the reports look like with sample data:

```bash
python demo_report.py
```

This will generate a beautiful report in `reports/demo_report.md` showing:
- 🔥 Hot and ❄️ cold team streaks
- ⭐ Standout player performances
- ⚠️ Injury updates
- 💰 Betting insights
- 👀 Must-watch matchups

## Generate Real Reports

### View Available Sports
```bash
python cli.py --list-sports
```

### Generate Full Report (All Sports)
```bash
python cli.py --all
```

### Single Sport Report
```bash
# Full detailed report
python cli.py --sports nfl

# Quick update
python cli.py --sports nba --quick
```

### Multiple Sports
```bash
python cli.py --sports nfl nba mlb
```

### Save to File
```bash
python cli.py --all --output today.md
```

## Automated Reports

Run scheduled reports (8 AM and 6 PM daily):

```bash
python scheduler.py
```

Test immediately:
```bash
python scheduler.py --test
```

## Slack Integration

1. Create a Slack Incoming Webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Create a webhook for your channel
   - Copy the webhook URL

2. Add to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. Run scheduler:
   ```bash
   python scheduler.py
   ```

Reports will automatically post to your Slack channel!

## Common Use Cases

### Morning Routine
Check all sports before starting your day:
```bash
python cli.py --all --output morning_briefing.md
```

### Game Day
Quick updates during NFL Sunday:
```bash
python cli.py --sports nfl --quick
```

### Multi-Sport Evening
Check results across major leagues:
```bash
python cli.py --sports nfl nba nhl mlb
```

### Set and Forget
Automated updates twice daily:
```bash
# Run in background
nohup python scheduler.py > scheduler.log 2>&1 &
```

## Troubleshooting

### ESPN API Issues
ESPN's unofficial API may occasionally block requests or be rate-limited. If you see "403 Forbidden" errors:

1. **Try again later** - Rate limits reset periodically
2. **Use the demo** - See `python demo_report.py` for sample output
3. **Check ESPN website** - If ESPN.com is down, the API won't work
4. **API changes** - ESPN may update their API; check for bot updates

The bot is designed to handle API failures gracefully and will work with whatever data is available.

### No Betting Data
Betting insights require a free API key from [The Odds API](https://the-odds-api.com/):

1. Sign up for free account (500 requests/month)
2. Get your API key
3. Add to `.env`: `ODDS_API_KEY=your_key_here`

Reports work fine without betting data - that section will just be skipped.

### Slack Not Posting
- Verify webhook URL is correct
- Test webhook with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test"}' \
    YOUR_WEBHOOK_URL
  ```
- Check Slack app permissions

## Next Steps

- **Customize sports**: Edit `config.py` to enable/disable leagues
- **Adjust schedule**: Modify `scheduler.py` for different times
- **Add more sports**: Extend the configuration
- **Create dashboards**: Use the reports in your own apps

## Need Help?

Check the full README.md for detailed documentation and examples!
