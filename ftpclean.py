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

def navigate_and_delete_files(remote_dir, ftp):
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

            if current_time > filetime + timedelta(hours=secrets.RETENTION_HOURS):
                number_of_files_left -= 1
                number_of_deleted_files += 1

                size_of_deleted_files += filesize
            
                # DELETE FILE HERE
                if not secrets.SIMULATE:
                    ftp.delete(remote_dir + '/' + file_name)
                
                print('DELETE FILE: ' + file_name)
            else:
                size_of_files_left += filesize

        # Checking directories
        if interesting_file[1]['type'] == 'dir':
            directory_name = interesting_file[0]
            number_of_directories += 1
            if directory_name not in secrets.EXCLUDED:
                result = navigate_and_delete_files(directory_name, ftp)

                # Remove folder if empty
                if result[1] == 0:
                    # DELETE FOLDER HERE
                    if not secrets.SIMULATE:
                        ftp.rmd(directory_name)
                    
                    print('DELETE FOLDER: ' + directory_name)

                print(f'Folder reviewed: {interesting_file[0]} , total files: {str(result[0])} , files after removal: {str(result[1])} , folders inside: {str(result[2])}')
           
    return (number_of_files_in_directory, number_of_files_left, number_of_directories)


def login_and_delete():
    # Your FTP Server credentials
    ftp = FTP(secrets.FTP_SERVER)
    ftp.login(secrets.FTP_USER, secrets.FTP_PASSWD)    
    result = navigate_and_delete_files('/', ftp)
    print(f'****** TOTALS ******\n- Files: {number_of_all_files}\n- Deleted: {number_of_deleted_files}\n- Directories = {result[2]}\n- Deleted size: {size_of_deleted_files//1024//1024} MB \n- Size left: {size_of_files_left//1024//1240} MB')
    ftp.quit()

def main():

    pulse = 0

    print('********* FTP CLEAN *********')    
    print(datetime.now())
    print('*****************************\n')    

    if len(sys.argv) < 2:
        login_and_delete()
        exit(1)

    try:
        pulse = int(sys.argv[1])
    except ValueError:
        print("Wrong argument. Must be digit (number of hours)")
        exit(1)

    while(True):
        login_and_delete()

        print(f'\nSleeping for {pulse} hours\n')
        time.sleep(pulse * 60 * 60)
    
if __name__ == "__main__":
    main()

