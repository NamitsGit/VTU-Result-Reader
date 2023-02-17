import pprint as pp
from pypdf import PdfReader
import re

# STEP 1 : Create a PDFReader object named 'reader'. 
#          This object enables us to use the functions associated with pypdf.
filepath = "samples/1.pdf"
reader = PdfReader(filepath)

# Uncomment the below 2 lines to verify the total number of pages in the pdf file
# number_of_pages = len(reader.pages)
# print("Total number of pages in the pdf file are : ",number_of_pages)

# STEP 2 : Create a page object from the first page of the pdf file. 

#          This is where we have our marks(typically within a table) to be read.
#          If the table extends from one page to more than one page we could put the page variable within a loop to
#          read the entire pdf file page-by-page and succesively append(concat) the extracted text to the contents 
#          variable(which is a string). 
#          After reading all the pages and appending the text, we have the content variable which has the entire 
#          content of the pdf file. 

#           Yaaaay!!!!

page = reader.pages[0]
content = page.extract_text()

# STEP 3 : Create a regular expression pattern for finding the Student Name. Now, there are limitless ways to do this
#          but the easiest way would be to use the label to capture anything that came after 'Student Name : ' and has
#          2 or optionally 3 words which contain only characters. And for this we use the re module.

#          So while doing this it is assumed that the student does not have special characters or numbers in their name.
#          Sorry, X Æ A-12.
#          But, if we want the program to be able to find names with special characters and if we know exactly what special 
#          characters might come in the name, we can give them in the character class of the name_regex.
#          After we're done finding the name we just store the match in the 'name' variable.

name_regex = "Student Name : ([A-Za-z]*\s[A-Za-z]*\s?[A-Za-z]*)"
name = re.search(name_regex,content).group(1)

# STEP 4 : Create a regular expression pattern for finding the University Seat Number/ Unique Student ID Number which is
#          present in all the reports. 
#          To do this I have used my University's regex below, it can find any string that has a digit which is followed
#          by any 2 alphabets, followed by any 2 digits again, then any 2 alphabets again and lastly ending with 3 digits.
#          This regex can be changed to meet the USN / other equivalent of your university.
#          This regex can find USNs/Student ID Nos. like 1AB23CS456
 
usn_regex = "(\d[A-Za-z]{2}\d{2}[A-Za-z]{2}\d{3})"
usn = re.search(usn_regex,content).group(1)

# Uncomment the below line to see the name and USN captured.
# print(name,usn,end="\n\n")

# We initialize like line_spill <list> which will be used to identify the subject names that have overflowed to the next
# line. This needs to be done if the subject code and marks are not on the same line.
line_spill = []

# We have the marks dictionary which will be used to store the marks in a systematic manner.
# Here we will have the subject code as the key used to access the internal, external and total marks. This is also used
# to store the result, which is usually a variable like P => Representing 'Pass' or F => Representing 'Fail' ...
marks = {}

# We have the data dictionary which will be used to store the entire data, which includes the student name, usn and marks.
# We are setting the default values of Student name, USN and Marks with the 'name', 'usn' and 'marks' variables.
data = {}
data.setdefault("Student Name",name)
data.setdefault("University Seat Number (USN)",usn)
data.setdefault("Marks",marks)

# STEP 5 : Split the entire string content into its lines and store all these lines within a list called 'lines'.
#          This step is used to convert an entire string block into a collection of seperate lines.
lines = content.split('\n')

# Print the lines below to check what see what is read by the pdf
# print(lines)
# print(len(lines))

# STEP 6 : Give the patterns for extracting the subject codes and marks.
#          The example of patterns for subject code which will be identified are 23CSL753.
#          The example of patterns for marks will be OVERFLOWED SUBJECT NAME (44 55 99 P)
#          where the first 1-3 digits represent the marks for internal exams,
#          next 1-3 digits represent the marks for external exams,
#          and then the total of these 2 marks.
#          The last character is usually used for identifying the (P)ass/(F)ail characters.
pattern_sub_code = '^(\d{2}[A-Za-z]{2,4}\d{2,3})'
pattern_marks = '[A-Za-z]*\s?(\d{1,3})\s(\d{1,3})\s(\d{1,3})\s([A-Z])'


# STEP 7 : Iterating over all the lines of the content string to find the patters in every line.
for line in lines:
    # for every new line assigning the Match Object (mo) for subject code and marks using the pattens given above.
    # print(line)
    mo_sub_code = re.search(pattern_sub_code,line)
    mo_marks = re.search(pattern_marks,line)

    # If we have both, the subject code and marks in the same line, then we can extract them in one shot.
    if(mo_sub_code != None and mo_marks != None):
        subject_code = mo_sub_code.group(1)
        internal_marks = int(mo_marks.group(1))
        external_marks = int(mo_marks.group(2))
        total_marks = int(mo_marks.group(3))
        result = mo_marks.group(4)
        if(subject_code not in marks.keys()):
            marks.setdefault(subject_code,{})
        marks[subject_code].setdefault("internal_marks",internal_marks)
        marks[subject_code].setdefault("external_marks",external_marks)
        marks[subject_code].setdefault("total_marks",total_marks)
        marks[subject_code].setdefault("result",result)
    
    # Else if we have only the subject code in the line and not the marks, it most possibly means that the 
    # subject name has overflown and the marks can be found while processing the next line. So just assign
    # the subject code and make a dictionary entry with the subject code as the key and set all the values of
    # marks and result for this subject code with default values.
    # Most important thing here is to add the spilled subject code to the line_spill list mentioned above.
    # In the next line we're going to use this subject code which was spilled, we have to do this because
    # while processing the next line, we will not have the subject code which is present one line before,
    # so we'll add the subject code to the line_spill list.
    elif(mo_sub_code != None and mo_marks == None):
        subject_code = mo_sub_code.group(1)
        if(subject_code not in marks.keys()):
            marks.setdefault(subject_code,{})
            marks[subject_code].setdefault("internal_marks",0)
            marks[subject_code].setdefault("external_marks",0)
            marks[subject_code].setdefault("total_marks",0)
            marks[subject_code].setdefault("result","")
            line_spill.append(subject_code)

    # Else if we have the marks pattern and not the subject code pattern, it means that this line contains the 
    # marks of the subject which was spilled in the previous line.
    # We populate the marks for the subject with which was most recently encountered with no marks pattern.
    # After this, we delete the subject code from the line_spill list. So at a time only one subject code
    # can be present in the line_spill list, whose contents have been spilled.
    elif(mo_sub_code == None and mo_marks != None):
        internal_marks = int(mo_marks.group(1))
        external_marks = int(mo_marks.group(2))
        total_marks = int(mo_marks.group(3))
        result = mo_marks.group(4)
        if len(line_spill) == 1:
            subject_code = line_spill[0]
            marks[subject_code]["internal_marks"] = internal_marks
            marks[subject_code]["external_marks"] = external_marks
            marks[subject_code]["total_marks"] = total_marks
            marks[subject_code]["result"] = result
            line_spill.pop()

# STEP 8 : Ta-Da!! And we're done extracting all the marks for all the subjects with their respective subject codes.
#          Now we sort the keys in alphabetical order for easier readablity.
#          We have successfully got the entire data which contains the student name, usn and marks.

# pprint.pprint(marks)
# pp.pprint(data)
sorted(data,reverse=True)
pp.pprint(data)
