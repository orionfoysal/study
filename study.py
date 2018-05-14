import json
import re
from selenium import webdriver 

driver = webdriver.Chrome('/home/clueless/chromedriver')
driver.get('')  


# Login to website 

name = driver.find_element_by_id('login')
name.send_keys('') 
pw = driver.find_element_by_id('pass')
pw.send_keys('')
links = driver.find_elements_by_xpath("//a[text() = 'Practice Test']")
submit = driver.find_element_by_xpath('//*[@id="home-hdr"]/div/div[2]/div/form/button')
submit.click()


# Get all the links of question sets 
tests_links = []
links = driver.find_elements_by_xpath("//a[text() = 'Practice Test']")
for link in links:
    h_link =link.get_attribute('href')
    tests_links.append(h_link)
    # print(h_link)


# Navigate to a question set
driver.get(tests_links[0])



Class = 'Previous_Questions'
Categoty = 'Non_Gov_Teacher_Reg_College'
Type = 'MCQ'
Exam_Name = 'BCS Preliminary Test'



#Loop through the all sets of questions 
for test_link in tests_links:
    driver.get(test_link)   #Navigate to the test page 
    
    print('Processing:',test_link)

    test_name = driver.find_element_by_xpath("//*[contains(@class, 'content-header')]").text
    Exam_Name = re.split('\(|\)', test_name)[1]
    fileName = test_link.split('/')[-1]+'.json'
  
    # Get all the questions
    questions = []
    q_links = driver.find_elements_by_xpath("//*[contains(@class, 'list-group-item list-ques')]")
    for q in q_links:
        questions.append(q.text)
        # print(q.text)

    total_questions = len(questions)

    # Get the options 
    options = []
    option = []
    op_links = driver.find_elements_by_xpath("//*[contains(@class, 'list-option')]")

    prev_q_number = 1
    for i,op in enumerate(op_links):
        q_number = int(op.find_element_by_xpath(".//input[@type = 'radio']").get_attribute('name').split('_')[-1])
        if q_number == prev_q_number:
            option.append(op.text)
        else:
            options.append(option)
            option = []
            option.append(op.text)
            prev_q_number = q_number
    # Append Last option list
    options.append(option)


    # Answers link and get answers
    answers = []
    ans_links = driver.find_elements_by_xpath("//*[contains(@class, 'list-hidden')]")
    for ans in ans_links:
        answer = ans.find_element_by_xpath(".//input[@type='hidden']").get_attribute('value')
        answers.append(answer)



    # Discussions on the questions 
    discussions = ['' for i in range(total_questions)]
    diss_links = driver.find_elements_by_xpath("//*[contains(@class, 'list-hint')]")
    for diss in diss_links:
        # diss_html = diss.get_attribute('innerHTML') # When javascript is disabled
        diss_html = diss.text # When javascript is disabled
        diss_index = int(diss.get_attribute('id').split('_')[-1])
        discussions[diss_index-1] = diss_html

    # Zip all lists to parse in dictionary
    f = zip(questions, options, answers, discussions)
    zipped_data = list(f)

    # Put all the data into a list of dictionay 
    diclist = []
    for q,o,a,h in zipped_data:
        data = {"byte":{"data":{"question": q,
                                "options": o,
                                "answer": a,
                                "hint": h,
                                "image_link":''
                            },
                            "info":{
                                "subject":'',
                                "topic":'',
                                "tags":[],
                                "difficulty_level":'',
                                "source":Exam_Name
                                }
                        }
            }
        diclist.append(data)
    

    writeable = {"meta":{"class": Class,
                "category": Categoty,
                "type": Type,
                "Exam_Name": Exam_Name
                },
            "all_data": diclist
            }


    #Dump data in dictionary format to json 
    with open('non_gov_teacher_college_'+fileName, 'w') as f:
        json.dump(writeable, f)
