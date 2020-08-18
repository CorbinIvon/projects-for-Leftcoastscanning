import os, os.path, sys
import time, datetime #For using time.sleep()
from selenium import webdriver
from EmailNotify import send_email
import colored

# ========== GLOBAL VARIABLES - USER MODIFIED ========== #
file_type_to_upload = [ ".tif" ]    # Will only upload files with this extension. Multiple extensions can be used.
laserfiche_folder_name = ""         # The folder on Laserfiche you want to upload to.
recursive_upload_directories_list = []   # A list of paths the recursion will look through.
physical_uploading_location = ""    #If an error occurs, The developer will be emailed, and will be in touch with you shortly.
# ========== GLOBAL VARIABLES - PRIVATE / PRE-SET - USED FOR CALCULATION ========== #
browser = None                      # The browser created through selenium
time_start = 0                      # Used to calculate how long it takes for the app to start
debug = False
wait_timer = 1
timer_wait_modifier = 0.5
exponential_wait_time = False
error_checking = False

def main():
    global recursive_upload_directories_list, browser, error_checking
    if not error_checking:
        try:
            initial_startup()
            for dir in recursive_upload_directories_list:
                start_recursive_process(dir, 0)
        except:
            error("Failed somewhere, Attempting to relaunch upload process.", "00")
            try: browser.quit()
            except: pass
            main()
        return
    else:
        initial_startup()
        for dir in recursive_upload_directories_list:
            start_recursive_process(dir, 0)
    input(colored.fg(3) + "All files have been uploaded.")
    time.sleep(3)
    browser.quit()

#Class btn btn-primary
#//*[@id="footerDiv"]/button[1]
# ========== NEW FUNCTIONS ========== #
def get_global_variables():
    global laserfiche_folder_name, recursive_upload_directories_list, physical_uploading_location
    if physical_uploading_location == "":
        physical_uploading_location = input("Who or where are you uploading from?\nEx. John or John's home\n--> ")
    print("Uploading as", physical_uploading_location)
    # Gets the Laserfiche folder name if none present.
    if laserfiche_folder_name == "":
        laserfiche_folder_name = input("Laserfiche Folder Name (The folder name on Laserfiche you wish to upload to.)(Must be exact spelling)\n--> ")
    # Continuouslt gets the directories if none present in the code.
    if len(recursive_upload_directories_list) == 0:
        print("Leave empty to confirm directories.")
        while 1:
            dir = input("Folder Directory: ")
            if dir == "":
                break
            recursive_upload_directories_list.append(dir)
    print ("Uploading directories to -->", laserfiche_folder_name, "<-- on Laserfiche:")
    for dirs in recursive_upload_directories_list:
        print(dirs)
    return
def initial_startup():
    print("NOTE: Please Keep Chrome Full Screened at ALL TIMES")
    seeder()
    get_global_variables()

    started_txt = "Started: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print (started_txt)
    write_text_to("", started_txt)
    open_chrome_and_navagate_to_main_area()
def read_file(file):
    #Returns a list of read lines
    list = []
    try:
        f = open(file, "r")
        list = f.read().split('\n')
    except:
        pass
    return list
def seeder():
    global laserfiche_folder_name, recursive_upload_directories_list, physical_uploading_location

    lst = read_file("Seeder.txt")
    rng = range(len(lst))
    if len(rng) > 2:
        laserfiche_folder_name = lst[0]
        physical_uploading_location = lst[1]
        for element in range(len(rng) - 2):
            recursive_upload_directories_list.append(lst[element + 2])
    print (laserfiche_folder_name)
    print (physical_uploading_location)
    print (recursive_upload_directories_list)
    return
def error(error_content, error_code):
    global physical_uploading_location
    #error_info = "ERROR CODE: 01\n   -Failed to upload file to Laserfiche.\nFile:", file_name, "\nDirectory:", file_directory, "\nThe file may have been too large or Laserfiche may have become unresponsive.\nScript Location: ", __file__
    send_email("", str("ERROR:" + physical_uploading_location + "- UploaderV2"), str("Error Code: " + str(error_code) + " | " + str(error_content)))
    write_text_to("", error_content)
    print(colored.fg(1), error_content)
    #print("ERROR CODE " + error_code + ":\nFAILED TO UPLOAD FILE, Exiting in 10 seconds.")
    #time.sleep(10)
    #browser.quit()
    #quit(1)
def retrieve_percent(attempt):
    global debug
    if debug:
        return
    progress_bar_length = 20
    percent_xpath = '//*[@id="UploadFormContainer"]/div[2]/table/tbody/tr/td[4]/span'
    percent_txt = '-1%'
    try: percent_txt = browser.find_element_by_xpath(percent_xpath).text
    except: pass
    percent_txt = percent_txt.replace('%','')
    if not percent_txt.isnumeric():
         percent_txt = '100'
    per_val = float(percent_txt)
    head = '[Waiting...: ' + str(attempt) + ']['
    fill = '='
    tail = ']'
    text = "\r{0}".format(head + fill * int(per_val / 10) + " " * int(11 - per_val / 10 - per_val / 100) + tail + percent_txt + '%')
    #text = "\r{0}".format(head + percent_txt + '%' + tail)
    #print(colored.fg(4))
    sys.stdout.write(colored.fg(3) + text)
    # sys.stdout.write("]")
    sys.stdout.flush()

# ========== HEAVILY MODIFIED FUNCTIONS ========== #
def start_recursive_process(current_directory, offset):
    global file_type_to_upload
    # Will go into sub-directories looking for files with the desired extension.
    for current_file in os.listdir(current_directory): # Gets just the name of the files, not the full directory
        if "Complete" not in current_file: # If it is not a " - Complete" folder, don't skip
            if os.path.isdir(current_directory + "\\" + current_file):
                print (current_file + " Is a directory. Scoping in.")
                start_recursive_process(current_directory + "\\" + current_file, 0)
            else:
                # Getting here means that it is a file. Make sure it has the target file extension
                is_correct_file = False
                for extension in file_type_to_upload: # Checks the file for the correct extension.
                    if extension in current_file:
                        is_correct_file = True
                        break
                if is_correct_file: # The file has the correct extension
                    #print ("Uploading >> " + current_directory + "\\" + current_file)
                    upload_file(current_directory, current_file)
                else:   #Not the correct file extension, ignoring and skipping
                    print(current_file + " does not have the correct file extension, skipping...")
    return
def upload_file(file_directory, file_name):
    global error_checking
    if not error_checking:
        try:
            hard_coded_upload_file(file_directory, file_name)
        except:
            error(("ERROR CODE: 01\n   -Failed to upload file to Laserfiche.\nFile:", file_name, "\nDirectory:", file_directory, "\nThe file may have been too large or Laserfiche may have become unresponsive.\nScript Location: ", __file__), "01")
            return upload_file(file_directory, file_name)
    else:
        hard_coded_upload_file(file_directory, file_name)
    return
def hard_coded_upload_file_old(file_path):
    global browser
    # Select upload button
    try:
        browser.find_element_by_xpath('//*[@id="footerDiv"]/button[1]').click()
        #print("Awsome...") # This is super dumb, but it works...
    except:pass
    wait_for_click_availability_xpath(browser, ['//*[@id="mainContainer"]/div[1]/div[5]/div/div/div[2]/div[1]/div[2]/span[4]/button'], 0)
    t1 = "Uploading >> " + file_path# + '\n'
    try:
        print(colored.fg(14) + t1)
    except:
        print(t1)
    write_text_to("", t1)
    # Upload File
    wait_for_availability_xpath(browser, ['//*[@id="ImportUploader"]/form/span[1]/input'], 0)
    time.sleep(1)
    send_keys_xpath(browser, ['//*[@id="ImportUploader"]/form/span[1]/input'], 0, file_path)
    time.sleep(1)
    # Click OK
    wait_for_click_availability_xpath(browser, ['//*[@id="footerDiv"]/button[1]'], 0)
    time.sleep(3)
    # Click Import - It sees it, but clicks it too fast, or clicks something entirely different...
    # Was this essential section that happened to fix everything for some reason? No. but it was essential for a wait process...
    wait_for_click_availability_xpath(browser, "//*[@id='generalTab']/div/div[2]/div[3]/div/div/select/option[3]", 0)
    #wait_for_click_availability_xpath(browser, '//*[@id="footerDiv"]/button[1]', 0)
    #time.sleep(3)
    return
#
# ========== CARRIED OVER FUNCTIONS ========== #
def hard_coded_upload_file(file_directory, file_name):
    global wait_timer
    # Wait for import
    wait_for_click_availability_xpath(browser, ['//*[@id="mainContainer"]/div[1]/div[5]/div/div/div[2]/div[1]/div[2]/span[4]/button'], 0)

    file_path = file_directory + "\\" + file_name
    #Log in txt file
    t1 = "Uploading >> " + file_path# + '\n'
    try:
        print(colored.fg(14) + t1)
    except:
        print(t1)
    write_text_to("", t1)

    # Send File Path
    send_keys_xpath(browser, ['//*[@id="ImportUploader"]/form/span[1]/input'], 0, file_path)
    # Click OK -> //*[@id="footerDiv"]/button[1] ->
    attempt = 0
    while 1:
        try:
            retrieve_percent(attempt)
            ok_btn = browser.find_element_by_xpath('/html/body/div[12]/div/div/div/div[3]/button[1]') #I am using the full xpath. This works well.
            ok_btn.click()
            break
        except:
            attempt += 1
            pass
        time.sleep(wait_timer)
    # Click Import -> //*[@id="footerDiv"]/button[1] ->
    time.sleep(wait_timer)
    print("\nImporting...")
    while 1:
        try:
            #import_btn = browser.find_element_by_xpath('//*[@id="footerDiv"]/button[1]')
            import_element = browser.find_element_by_xpath('/html/body/div[12]/div/div/div/div[4]/button[1]') #I am using the full xpath. This works well.
            import_element.click()
            break
        except:
            try:
                # Deals with the Name Conflict
                other_element = browser.find_element_by_xpath('/html/body/div[12]/div/div/div/div[2]/div')
                ok_btn = browser.find_element_by_xpath('/html/body/div[12]/div/div/div/div[3]/button[1]')
                ok_btn.click()
            except: pass
        time.sleep(wait_timer)
    #wait_for_click_availability_xpath(browser, '//*[@id="footerDiv"]/button[1]', 0)
    #input("Simulate Imported Event")
    while 1:
        try:
            complete_element = browser.find_element_by_xpath('/html/body/div[2]/div[1]/div[4]/div/div') #I am using the full xpath. This works well.
            break
        except:
            #print("Can not find complete...")
            #skp = input("skip?")
            time.sleep(wait_timer)
    # Figure out how to wait for import to complete
    #print("Before move")
    #print(file_directory, file_name)
    move_file(file_directory, file_name)
    #inp = input("Continue?")

def open_chrome_and_navagate_to_main_area():
    global time_start, browser
    if browser != None:
        browser.quit()
    browser = webdriver.Chrome()    # Opens the browser
    browser.maximize_window()       # Maximizes the window

    time_start = time.perf_counter()
    ### SETUP ###
    laser_id = ""
    laser_username=""
    laser_pass=""
    Laserfiche_Login_URL = "https://accounts.laserfiche.com/"
    # Opens chrome to laserfiche login #
    browser.get(Laserfiche_Login_URL)
    # Acount ID #
    wait_for_availability_id(browser, "customerIDField", 0)
    browser.find_element_by_id("customerIDField").send_keys(laser_id)
    browser.find_element_by_id("nextBtn").click()
    # Login info
    wait_for_availability_id(browser, "nameField", 0)
    #browser.find_element_by_id("nameField").send_keys(laser_username)
    wait_for_send_availability_id(browser, "nameField", 0, laser_username)
    browser.find_element_by_id("passwordField").send_keys(laser_pass)
    browser.find_element_by_id("loginBtn").click()
    # Naviagte to repository
    wait_for_click_availability_id(browser, "appPickerTrigger", 0)
    wait_for_click_availability_link(browser, "Documents", 0)
    # Select folder for uploading to
    global laserfiche_folder_name
    wait_for_click_availability_link(browser, laserfiche_folder_name, 0)
    t1 = "Startup Time: " + str(time.perf_counter() - time_start)
    try:
        print(colored.fg(7) + t1)
    except:
        print(t1)
    write_text_to("", t1)
    return
def write_text_to(log_path, string):
    if log_path == "":
        logs_path = ""r"Logs\\"
    try:
        f = open (logs_path + "Upload Log " + datetime.datetime.now().strftime("%Y-%m-%d.txt"), "r")
        f.close()
    except:
        file = open (logs_path + "Upload Log " + datetime.datetime.now().strftime("%Y-%m-%d.txt"), "w+")
        # Initial File Message #
        file.write("File Upload Log - This file keeps track of the thing tha thave been uploaded.")
        # Close to save
        file.close()
        
    f = open (logs_path + "Upload Log " + datetime.datetime.now().strftime("%Y-%m-%d.txt"), "a")
    f.write("\n" + str(string))
    f.close()
    return
def create_custom_dir(path, added_extension):
    # Creates a new folder, right under the current path to move files to.
    new_dir = path + added_extension
    if not os.path.exists(new_dir):
        t1 = "[New Directory Created] >> " + new_dir
        try:
            print(colored.fg(3), t1)
        except:
            print(t1)
        write_text_to("", t1)
        os.makedirs(new_dir)
    return new_dir
def move_file(file_from_dir, file_name):
    file_to_dir = create_custom_dir(file_from_dir, " - Complete")
    curr_path = file_from_dir + "\\" + file_name
    new_path = file_to_dir + "\\" + file_name
    os.rename(curr_path, new_path)

    print (colored.fg(3), "Moved : " + file_name + " >> " + new_path)
    return
def import_documet_settings():
    global browser
    # Click the Cume option
    #wait_for_click_availability_xpath(browser, "//*[@id='generalTab']/div/div[2]/div[3]/div/div/select/option[3]",0)
    # Click Import
    wait_for_click_availability_xpath(browser, '//*[@id="footerDiv"]/button[1]', 0)
    #browser.find_element_by_xpath("//*[@id='footerDiv']/button[1]").click()
    #browser.find_element_by_xpath('//*[@id="footerDiv"]/button[1]').click()
    wait_for_click_availability_xpath(browser, '//*[@id="footerDiv"]/button[1]', 0)
    return

# ========== SELENUIM SPECIFIC FUNCTIONS ========== #
def send_keys_xpath(browser, xpath_list, count, file_path):
    global timer_wait_modifier, exponential_wait_time
    if exponential_wait_time:
        time.sleep(count * timer_wait_modifier)
    else:
        time.sleep(timer_wait_modifier)

    size = len(xpath_list)
    for n in range(size):
        try:
            browser.find_element_by_xpath(xpath_list[n]).send_keys(file_path)
            return
        except:
            pass
    global debug
    if debug:
        print("[" + str(count) + "]" + " Waiting to send path >> " + str(xpath_list))

    return send_keys_xpath(browser, xpath_list, count + 1, file_path)

def wait_for_availability_xpath(browser, xpath_list, count):
    global timer_wait_modifier, exponential_wait_time
    if exponential_wait_time:
        time.sleep(count * timer_wait_modifier)
    else:
        time.sleep(timer_wait_modifier)
    size = len(xpath_list)
    for n in range(size):
        try:
            browser.find_element_by_xpath(xpath_list[n])
            return
        except:
            pass
    global debug
    if debug:
        print("[" + str(count) + "]" + " Waiting for xpaths >> " + str(xpath_list))
    return wait_for_availability_xpath(browser, xpath_list, count + 1)
def wait_for_click_availability_xpath(browser, xpath_list, count):
    global timer_wait_modifier, exponential_wait_time
    if exponential_wait_time:
        time.sleep(count * timer_wait_modifier)
    else:
        time.sleep(timer_wait_modifier)
    size = len(xpath_list)
    for n in range(size):
        try:
            browser.find_element_by_xpath(xpath_list[n]).click()
            return
        except: pass
    global debug
    if debug:
        print("[" + str(count) + "]" + " Waiting for xpaths >> " + str(xpath_list))
    retrieve_percent(count)
    return wait_for_click_availability_xpath(browser, xpath_list, count + 1)
def check_for_availability_xpath(browser, xpath):
    while 1:
        try:
            browser.find_element_by_xpath(xpath)
            return True
        except:
            return False

def wait_for_availability_id(browser, id, count):
    global timer_wait_modifier, exponential_wait_time
    while 1:
        try:
            if exponential_wait_time:
                time.sleep(count * timer_wait_modifier)
            else:
                time.sleep(timer_wait_modifier)
            browser.find_element_by_id(id)
            return True
        except:
            global debug
            if debug:
                print("[" + str(count) + "]" + " Waiting for id >> " + id)
            return wait_for_availability_id(browser, id, count+1)
        return
def wait_for_send_availability_id(browser, id, count, keys):
    global timer_wait_modifier, exponential_wait_time
    while 1:
        try:
            if exponential_wait_time:
                time.sleep(count * timer_wait_modifier)
            else:
                time.sleep(timer_wait_modifier)
            browser.find_element_by_id(id).send_keys(keys)
            return True
        except:
            global debug
            if debug:
                print("[" + str(count) + "]" + " Waiting for id >> " + id)
            return wait_for_send_availability_id(browser, id, count+1, keys)
        return
def wait_for_click_availability_id(browser, id, count):
    global timer_wait_modifier, exponential_wait_time
    while 1:
        try:
            if exponential_wait_time:
                time.sleep(count * timer_wait_modifier)
            else:
                time.sleep(timer_wait_modifier)
            browser.find_element_by_id(id).click()
            return True
        except:
            global debug
            if debug:
                print("[" + str(count) + "]" + " Waiting for id >> " + id)
            return wait_for_click_availability_id(browser, id, count+1)
        return
def check_for_availability_id(browser, id):
    while 1:
        try:
            browser.find_element_by_id(id)
            return True
        except:
            return False

def wait_for_availability_link(browser, link_text, count):
    global timer_wait_modifier, exponential_wait_time
    while 1:
        try:
            if exponential_wait_time:
                time.sleep(count * timer_wait_modifier)
            else:
                time.sleep(timer_wait_modifier)
            browser.find_element_by_link_text(link_text)
            return True
        except:
            global debug
            if debug:
                print("[" + str(count) + "]" + " Waiting for link_text >> " + link_text)
            return wait_for_availability_link(browser, link_text, count+1)
        return
def check_for_availability_link(browser, link_text):
    while 1:
        try:
            browser.find_element_by_link_text(link_text)
            return True
        except:
            return False
def wait_for_click_availability_link(browser, link_text, count):
    global timer_wait_modifier, exponential_wait_time
    while 1:
        try:
            if exponential_wait_time:
                time.sleep(count * timer_wait_modifier)
            else:
                time.sleep(timer_wait_modifier)
            browser.find_element_by_link_text(link_text).click()
            return True
        except:
            global debug
            if debug:
                print("[" + str(count) + "]" + " Waiting for link_text >> " + link_text)
            return wait_for_click_availability_link(browser, link_text, count+1)
        return

def wait_for_click_availability_class(browser, classs, count):
    global timer_wait_modifier, exponential_wait_time
    if exponential_wait_time:
        time.sleep(count * timer_wait_modifier)
    else:
        time.sleep(timer_wait_modifier)
    try:
        browser.find_element_by_class_name(classs).click()
        return
    except:
        global debug
        if debug:
            print("[" + str(count) + "]" + " Waiting for class >> " + classs)
        browser.find_element_by_class_name(classs).click()
        return wait_for_click_availability_class(browser, classs, count+1)
    return

# ========== START ========== #
if not error_checking:
    try:
        main()
    except:
        send_email('', "FATAL ERROR: " + physical_uploading_location, "Could not recover from error. A manual restart is necessary.")
        print("ERROR CODE " + "FATAL" + ":\nFAILED TO UPLOAD FILE, Exiting in 10 seconds.")
        time.sleep(10)
        browser.quit()
        quit(-1)
    quit(0)
else:
    main()
