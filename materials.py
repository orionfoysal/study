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
hrefs = []
tags = driver.find_elements_by_xpath("//li/a")

breaks = {0:'BCS', 10:'BANK', 19:'BCS_Written', 28: 'MBA', 32:'PSC_and_GOV', 40:'Advocate', 47:'IT', 52:'Non_Gov_Teacher_Reg_P1', 56:'Non_Gov_Teacher_Reg_P2', 60:'Non_Gov_Teacher_Reg_College', 64:'Primary_School',70:'Special_BCS'}
for i in tags:
    hrefs.append(i.get_attribute('href'))

hrefs = hrefs[19:]
tags = tags[19:]

subjects = [i.text for i in tags]

for i,href in enumerate(hrefs):

    subject = subjects[i]
    Exam_Name = 'Practice'
    source = 'StudyPress'
    Type = 'MCQ'
    Class = 'Practice_Questions'
    if i in breaks:
        Category = breaks[i]

    # Navigate to a question set
    driver.get(href)


    tests_links = []
    tests_elements = driver.find_elements_by_xpath("//a")
    links = [link for link in tests_elements if 'Start Practice' in link.text]
    for i in links:
        tests_links.append(i.get_attribute('href'))
    
    # tests_links = [str(link) for link in tests_links if 'Start Practice' in link.text]
    #Loop through the all sets of questions 
    for test_link in tests_links:

        try:

            driver.get(test_link)   #Navigate to the test page 

            topic = driver.find_element_by_xpath("//h4[@class = 'bx-title']").text
            topic = topic.split('-')[-1]
            
            print('Processing:',test_link)

            test_name = driver.find_element_by_xpath("//*[contains(@class, 'content-header')]").text
            # Exam_Name = re.split('\(|\)', test_name)[1]
            fileName = test_link.split('/')[-1]+'.json'
        
            # Get all the questions
            questions = []
            source = []
            q_links = driver.find_elements_by_xpath("//*[contains(@class, 'list-group-item list-ques')]")
            for q in q_links:
                ques = q.text
                if '\n' in ques:
                    ques = ques.splitlines()
                    source.append(ques[-1])
                    ques = ques[0]
                else:
                    source.append('StudyPress')
                questions.append(ques)
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
            f = zip(questions, options, answers, discussions, source)
            zipped_data = list(f)

            # Put all the data into a list of dictionay 
            diclist = []
            for q,o,a,h,s in zipped_data:
                data = {"byte":{"data":{"question": q,
                                        "options": o,
                                        "answer": a,
                                        "hint": h,
                                        "image_link":''
                                    },
                                    "info":{
                                        "subject": '',
                                        "topic": subject,
                                        "tags":[topic],
                                        "difficulty_level":'',
                                        "source": s
                                        }
                                }
                    }
                diclist.append(data)
            

            writeable = {"meta":{"class": Class,
                        "category": Category,
                        "type": Type,
                        "Exam_Name": topic
                        },
                    "all_data": diclist
                    }


            #Dump data in dictionary format to json 
            with open(Category+ '_Practice_' +fileName, 'w') as f:
                json.dump(writeable, f)


        except:
            print('######### Failed',test_link)
            with open('failed.txt','a') as f:
                f.write(test_link+'\n')

