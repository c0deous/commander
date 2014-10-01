#!/usr/bin/env python3
# encoding: utf-8
"""
commander.py

Created by Jesse Wallace on 2014-08-27.
Copyright (c) 2014 Imaginary Pixels All rights reserved.
"""

import sys, os, cmd, sqlite3, getpass, os.path
from optparse import OptionParser
from bs4 import BeautifulSoup
from passlib.apps import custom_app_context as pwd_context

def main():
    # Options
    parser = OptionParser()
    parser.add_option('-l', '--login', dest='user', help='User to login with')
    parser.add_option('-r', '--register', dest='register_opt', action="store_true", default=False, help='Starts Registration Process')
    
    (options, args) = parser.parse_args()
    if options.user:
        username = options.user
    else:
        username = ""
    #Default Profile
    profile_default = """<?xml version="1.0" encoding="UTF-8"?>
<profile>
        <full_name>Name</full_name>
        <age>Age</age>
        <bio>
            Something to describe you
        </bio>
        <website>Link to your website (if any)</website>
        <irc>
                <server>Your favorite IRC Server</server>
                <channel>Your favorite IRC Channel</channel>
        </irc>
</profile>
"""
    # Initiation
    def initCommander(user):
        auth_dict = {} #wipe authentication dictionary for security
        CommanderLine().cmdloop()
    
    # Get User Profile
    def getprofile(userlookup):
        try:
            conn = sqlite3.connect('commander.db')
            cur = conn.cursor() 
            cur.execute("SELECT FULL_NAME, AGE, BIO, WEBSITE, IRC_SERVER, IRC_CHANNEL FROM profiles WHERE NICKNAME LIKE '%  " + userlookup + " %' OR NICKNAME like '" + userlookup + " %' OR NICKNAME like '" + userlookup + "';")
            conn.commit()
            
            profile = cur.fetchone()
            
            full_name = profile[0]
            age = profile[1]
            bio = profile[2]
            website = profile[3]
            irc_server = profile[4]
            irc_channel = profile[5]
            print(full_name + " " + userlookup)
            print(" ")
            print("____________________________")
            print(str(age) + " years of age")
            print(" ")
            print(bio)
            print(" ")
            print(website)
            print("IRC: " + irc_server + " - " + irc_channel)
            print(" ")
        except TypeError:
            print("[+] Couldn't find profile for " + userlookup)
#Update User Profile
    def updateprofile(profilepath):
        profilepath_e = os.path.expanduser(profilepath)
        if os.path.isfile(profilepath_e) == True:
            print('[*] Parsing ' + profilepath)
            profile_f = open(profilepath_e, 'r')
            profile_f = profile_f.read()
            soup = BeautifulSoup(profile_f)
            p_age = soup.age.string
            p_name = soup.full_name.string
            p_bio = soup.bio.string
            p_web = soup.website.string
            p_irc_server = soup.irc.server.string
            p_irc_channel = soup.irc.channel.string
            
            # Data Length Check
            if len(p_name) > 25:
                print('[-] Name is more than 25 characters. Please limit to 25 characters or less.')
            elif len(p_age) > 3:
                print('[-] Nobody is that old :D.  Quit lying and please change the age to 3 long digits or less.')
            elif len(p_bio) > 160:
                print('[-] Please limit your bio to 160 characters or less.  Currently it is ' + len(p_bio) + ' characters long.')
            elif len(p_web) > 70:
                print('[-] Please limit your web address to 70 characters or less.')
                print('[*] If your web address happens to be more than 70 characters long, consider using bit.ly or another url shortener.')
            elif len(p_irc_server) > 70:
                print('[-] Please limit your IRC Server to 70 characters or less.')
            elif len(p_irc_channel) > 35:
                print('[-] Please limit your IRC Channel to 35 characters or less.')
            else:  
                # Review Data
                print('Name: ' + p_name)
                print('Age: ' + p_age)
                print('Bio: ' + p_bio)
                print('Website: ' + p_web)
                print('IRC Server: ' + p_irc_server)
                print('IRC Channel: ' + p_irc_channel)
                print
                update_q = input('[*] Update profile with this information? [y/n] ')
                if update_q == 'y':
                    conn = sqlite3.connect('commander.db')
                    cur = conn.cursor()
                    cur.executescript("UPDATE profiles SET FULL_NAME='" + p_name +"', AGE='" + p_age + "', BIO='" + p_bio + "', WEBSITE='" + p_web + "', IRC_SERVER='" + p_irc_server + "', IRC_CHANNEL='" + p_irc_channel + "' WHERE NICKNAME='" + username + "'")
                    conn.commit()
                elif update_q == 'n':
                    pass
                else:
                    print('[-] Please type either "y" or "n"')
            
        else:
            print('[-] No profile exists at ' + profilepath)
    def manual_edit_profile(profilepath):
        profilepath_e = os.path.expanduser(profilepath)
        if os.path.isfile(profilepath_e) == True:
            os.system('nano ' + profilepath_e)
        else:
            print('[-] No Profile exists at ' + profilepath)
            edit_q = input('[*] Do you want to create one at the path you gave me? [y/n] ')
            if edit_q == 'y':
                new_profile = open(profilepath_e, 'w')
                new_profile.write(profile_default)
                new_profile.close()
                print('[+] New Profile created successfully!')
                print('[*] Opening...')
                os.system('nano ' + profilepath_e)           
            else:
                pass

    # Interactive command line
    class CommanderLine(cmd.Cmd):
        prompt = '[cmdr] | '
        intro = 'Welcome to Commander, ' + username + '. Type "help" for help'
        #Search related stuff    
        def do_search(self, line):
            print("Search function") #wip
        #Profile Related Stuff    
        def do_update_profile(self, line):
            if line:
                updateprofile(line)
            else:
                path = "~/.commander/profile.xml"
                updateprofile(path)

        def do_edit_profile(self, line):
            if line:
                edit_profile(line)
            else:
                edit_profile('~/.commander/profile.xml')
        
        def do_profile(self, line):
            if line == "":
                getprofile(username)
            else:
                getprofile(line)

        def do_manual_edit_profile(self, line):
            if line:
                manual_edit_profile(line)
            else:
                manual_edit_profile('~/.commander/profile.xml')
        # Navigation and organization stuff
        def do_clear(self, line):
            os.system('clear')  
        
        def emptyline(self):
            pass

        def do_exit(self, line):
            exit()      
        
    
    # Authentication
    def login(givenuser = ""):
        print('Authenticating ...')
        cursor = conn.execute("SELECT username, password from users")
        auth_dict = {}
        for row in cursor:
            auth_dict[row[0]] = row[1]
        if givenuser:
            user = givenuser
        else:
            user = input('Username: ')
        password = getpass.getpass()
    
        if user in auth_dict:
            if pwd_context.verify(password, auth_dict[user]) == True:
                print('Authenticated!')
                initCommander(user)
                
                
            else:
                print('Bad user or pass')
                exit()
        else:
            print('Bad user or pass')
            exit()
    
    def register(reg_full_name = "", reg_username = "", reg_password = "", reg_vpassword = "", reg_age = ""):
        #Load Userlist so two people can't have the same username
        cursor = conn.execute("SELECT username from users")
        user_list = []
        for row in cursor:
            user_list.append(row[0])


        if reg_full_name:
            pass
        else:
            reg_full_name = input('Full name: ')
        if reg_username:
            pass
        else:
            reg_username = input('Username: ')
        # Check for same username
        if reg_username in user_list:
            print('[-] That user already exists!')
            register(reg_full_name)
            
        if reg_password:
            pass
        else:
            reg_password = getpass.getpass()
        if reg_vpassword:
            pass
        else:
            reg_vpassword = getpass.getpass('Verify Password: ')
        
        if reg_password == reg_vpassword:
            reg_password_hash = pwd_context.encrypt(reg_password)
        else:
            print("Passwords don't match")
            register(reg_full_name, reg_username)
        if reg_age:
            pass
        else:
            reg_age = input('Age: ')
            
        # Add info to DB 

        cur = conn.cursor()
        cur.executescript("""INSERT INTO users (username, password)
        VALUES ('""" + reg_username + """', '""" + reg_password_hash + """');
        INSERT INTO profiles (NICKNAME, FULL_NAME, AGE, BIO, WEBSITE, IRC_SERVER, IRC_CHANNEL)
        VALUES ('""" + reg_username + """', '""" + reg_full_name + """', '""" + reg_age + """', 'n/a', 'n/a', 'n/a', 'n/a'); """)
        conn.commit()
        
        # Notify and Login
        print("[+] Registration Sucessful!")
        print("[*] Now run 'commander -l " + reg_username + "' to login")
        

    #connect to database
    conn = sqlite3.connect('commander.db')
    print('Connecting to database ...')
    
    # Launch
    if options.user:
        if options.register_opt == False:
            login(options.user)
        elif options.register_opt == True:
            print("Can't combine the -l and -r options")
        
    elif options.register_opt == True:
        register()
    else:
        print("[-] Please either login (-l) or register (-r)")

if __name__ == '__main__':
    main()
