###################################################################
#
# ftpclean.py <retention time> <time period>
# 
# parameters:
#  - retention time - minimum age of files in hours to be deleted
#  - time period - waiting time in hours between each execution
###################################################################


import secrets
import sys
import time
from datetime import datetime, timedelta
from dateutil import parser
from ftplib import FTP


current_time = datetime.now()
number_of_all_files = 0
number_of_deleted_files = 0
size_of_files_left = 0
size_of_deleted_files = 0

def log(input):
    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
    print(t + input)


def navigate_and_delete_files(remote_dir, ftp, retention, debug):
    number_of_files_left = 0
    number_of_files_in_directory = 0
    number_of_directories = 0
    global number_of_deleted_files
    global number_of_all_files
    global size_of_files_left
    global size_of_deleted_files

    directory_listing = ftp.mlsd(remote_dir)
    for interesting_file in directory_listing:
        file_name = interesting_file[0]

        # Checking and deleting files
        if interesting_file[1]['type'] == 'file':
            number_of_files_left += 1
            number_of_files_in_directory += 1
            number_of_all_files += 1
        
            timestamp = interesting_file[1]['modify']
            filetime = parser.parse(timestamp)
            filesize = int(interesting_file[1]['size'])

            if debug:
                log(f'Lookup file : {timestamp} size: {filesize} time: {filetime} ')

            if current_time > filetime + timedelta(hours=retention):
                number_of_files_left -= 1
                number_of_deleted_files += 1

                size_of_deleted_files += filesize
            
                # DELETE FILE HERE
                if not secrets.SIMULATE:
                    ftp.delete(remote_dir + '/' + file_name)
                                
                log('DELETE FILE: ' + file_name)
            else:
                size_of_files_left += filesize

        # Checking directories
        if interesting_file[1]['type'] == 'dir':
            directory_name = interesting_file[0]
            number_of_directories += 1
            if directory_name not in secrets.EXCLUDED:
                result = navigate_and_delete_files(directory_name, ftp, retention, debug)

                # Remove folder if empty
                if result[1] == 0:
                    # DELETE FOLDER HERE
                    if not secrets.SIMULATE:
                        ftp.rmd(directory_name)
                    
                    #print('DELETE FOLDER: ' + directory_name)
                    log('DELETE FOLDER: ' + directory_name)

                #print(f'Folder reviewed: {interesting_file[0]} , total files: {str(result[0])} , files after removal: {str(result[1])} , folders inside: {str(result[2])}')
                log(f'Folder reviewed: {interesting_file[0]} , total files: {str(result[0])} , files after removal: {str(result[1])} , folders inside: {str(result[2])}')
           
    return (number_of_files_in_directory, number_of_files_left, number_of_directories)


def login_and_delete(retention, debug = False):
    # Your FTP Server credentials

    ftp = FTP(secrets.FTP_SERVER)
    ftp.login(secrets.FTP_USER, secrets.FTP_PASSWD)    
    result = navigate_and_delete_files('/', ftp, retention, debug)
    print(f'****** SUMMARY ******\n- Retention: {str(retention)}\n- Debug: {str(debug)}\n- Simulate: {str(secrets.SIMULATE)}')
    print(f'****** TOTALS ******\n- All files: {number_of_all_files}\n- Deleted files: {number_of_deleted_files}\n- Reviewed directories: {result[2]}\n- Deleted size: {size_of_deleted_files//1024//1024} MB \n- Size left: {size_of_files_left//1024//1240} MB')
    print(f'********************')
    ftp.quit()

def main():

    pulse = 0
    retention = secrets.RETENTION_HOURS
    debug = False

    print('********* FTP CLEAN *********')    
    print(f'Time: {datetime.now()}')
    print('*****************************')
    if secrets.SIMULATE:
        print('*** SIMULATION ***')


    # Get arguments
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        try:
            retention = int(sys.argv[1])
        except ValueError:
            print("Wrong argument. Must be digit (number of hours)\nftpclean.py <retention time> <time period> <DEBUG>")
            exit(1)
    elif len(sys.argv) == 3:
        try:
            retention = int(sys.argv[1])
            pulse = int(sys.argv[2])
        except ValueError:
            print("Wrong argument. Must be digit (number of hours)\nftpclean.py <retention time> <time period> <DEBUG>")
            exit(1)
    elif len(sys.argv) == 4:
        try:
            retention = int(sys.argv[1])
            pulse = int(sys.argv[2])
            if sys.argv[3] == "DEBUG":
                debug = True
        except ValueError:
            print("Wrong argument. Must be digit (number of hours)\nftpclean.py <retention time> <time period> <DEBUG>")
            exit(1)

    else:
        print("Wrong number of arguments. Must be digit (number of hours).\nftpclean.py <retention time> <time period> <DEBUG>")
        exit(1)

    print(f'Pulse: {str(pulse)}')    
    print(f'Retention: {str(retention)}')
    print('*****************************\n')

    # Execute application
    if pulse == 0:
        login_and_delete(retention, debug)
        print('Closing application')        
    else:
        while(True):
            login_and_delete(retention, debug)

            print(f'\nSleeping for {pulse} hours\n')
            time.sleep(pulse * 60 * 60)
    
if __name__ == "__main__":
    main()

