# recipe-list-py
Program to save and list recipes using dropbox, excel and python

Made for my workplace trial, where we couldn't use a real database, so the program uses Dropbox as a bootleg database.
I made an otherwise unused dropbox account just for the program

How everything works:
The program checks your dropbox for a recipes.csv file, downloads and opens it. Once you're done using the program, if you've made any changes to the recipe list (Added/edited/deleted), the program removes the old file, and uploads the new one. Not intended to be used by multiple people at once.

Has an additional program to get your refresh key, since dropbox keys only last for 4 hours.

If you wish to use this for some reason what you need is: 
1. A Dropbox account
2. A Working internet connection
3. A blank .csv file

Steps to make this work:
1. Create a Dropbox account, or if you already have one, log in. Drop your "recipes.csv" into your dropbox
2. Go to https://www.dropbox.com/developers and create an app, name it whatever you want, give it permissions to read and write your files
3. Get your app_key and app_secret from your app info, add these to your recipe-list.py
4. Launch get-refresh-token.py and follow its instructions, in the end you will get a bunch of info, in it is your refresh token: put it into the refresh_token field in recipe-list.py
5. Launch recipe-list.py: It should work :D

