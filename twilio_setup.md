# Twilio Setup Guide

1. Log in to Twilio Console
2. Go to Phone Numbers → Active Numbers → Click your number
3. Under "Voice & Fax", set:
   - A Call Comes In: Webhook
   - Method: POST
   - URL: https://your-app-url.onrender.com/process_twilio_audio

4. Save and call your Twilio number